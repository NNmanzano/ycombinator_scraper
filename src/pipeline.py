"""
Orchestrator: wires the three stages together and keeps the run going even
when individual companies fail (a broken company page shouldn't kill a
165-company run, it gets logged and the run continues).
"""
import json
from typing import Optional

from . import config
from .algolia_client import AlgoliaCompanyListClient
from .detail_scraper import CompanyDetailScraper
from .exporter import ExcelExporter
from .logger import get_logger
from .models import Company

log = get_logger(__name__)


class YCombinatorPipeline:
    def __init__(
        self,
        batches: Optional[list[str]] = None,
        headless: bool = config.HEADLESS,
        limit: Optional[int] = None,
    ):
        self.batches = batches or config.DEFAULT_BATCHES
        self.headless = headless
        self.limit = limit

    async def run(self) -> list[Company]:
        hits = AlgoliaCompanyListClient(self.batches).fetch()
        if self.limit:
            hits = hits[: self.limit]
            log.info("Limiting run to first %d companies", self.limit)

        companies: list[Company] = []
        failed_slugs: list[str] = []

        async with CompanyDetailScraper(headless=self.headless) as scraper:
            for i, hit in enumerate(hits, start=1):
                slug = hit["slug"]
                log.info("[%d/%d] Scraping %s", i, len(hits), slug)
                company = await scraper.scrape(
                    slug=slug, name=hit["name"], website=hit.get("website", "")
                )
                if company.scrape_error:
                    failed_slugs.append(slug)
                companies.append(company)

        ExcelExporter.export(companies)

        config.DATA_DIR.mkdir(parents=True, exist_ok=True)
        with open(config.FAILED_SLUGS_JSON, "w", encoding="utf-8") as fh:
            json.dump(failed_slugs, fh, indent=2)
        if failed_slugs:
            log.warning("%d companies failed, see %s", len(failed_slugs), config.FAILED_SLUGS_JSON)

        log.info("Done: %d companies -> %s", len(companies), config.EXCEL_OUTPUT)
        return companies
