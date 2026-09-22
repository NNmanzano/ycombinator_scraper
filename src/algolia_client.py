"""
Stage 1: get the list of companies for the requested batches out of YC's
Algolia-backed search API. Plain requests, this endpoint returns JSON
directly, no browser rendering involved.
"""
import json
import re
from typing import Optional
from urllib.parse import quote

import requests

from . import config
from .logger import get_logger

log = get_logger(__name__)


class AlgoliaCompanyListClient:
    def __init__(self, batches: Optional[list[str]] = None):
        self.batches = batches or config.DEFAULT_BATCHES

    def _resolve_credentials(self) -> tuple[str, str]:
        """YC rotates its public Algolia search key periodically (the app id
        stays put). Scrape the current key out of the companies page instead
        of trusting a value that will eventually go stale."""
        try:
            resp = requests.get(
                config.YC_COMPANIES_PAGE,
                timeout=15,
                headers={"User-Agent": "Mozilla/5.0"},
            )
            resp.raise_for_status()
            match = re.search(r"window\.AlgoliaOpts\s*=\s*(\{.*?\});", resp.text)
            if match:
                opts = json.loads(match.group(1))
                log.debug("Resolved live Algolia credentials from companies page")
                return opts["app"], opts["key"]
        except Exception as exc:
            log.warning("Could not resolve live Algolia key (%s); using fallback", exc)
        return config.ALGOLIA_APP_ID, config.ALGOLIA_API_KEY_FALLBACK

    def fetch(self) -> list[dict]:
        app_id, api_key = self._resolve_credentials()
        facet_filters = json.dumps([[f"batch:{b}" for b in self.batches]])
        params = {
            "x-algolia-agent": "Algolia for JavaScript (4.14.2); Browser",
            "x-algolia-application-id": app_id,
            "x-algolia-api-key": api_key,
        }
        query_params = (
            f"facetFilters={quote(facet_filters)}&hitsPerPage=1000&page=0&query="
        )
        payload = {
            "requests": [{"indexName": config.ALGOLIA_INDEX, "params": query_params}]
        }

        log.info("Fetching company list for batches=%s", self.batches)
        response = requests.post(
            config.ALGOLIA_SEARCH_URL, params=params, json=payload, timeout=30
        )
        response.raise_for_status()

        hits = response.json()["results"][0]["hits"]
        log.info("Fetched %d companies", len(hits))

        config.DATA_DIR.mkdir(parents=True, exist_ok=True)
        with open(config.RAW_COMPANIES_JSON, "w", encoding="utf-8") as fh:
            json.dump(hits, fh, indent=2, ensure_ascii=False)

        return hits
