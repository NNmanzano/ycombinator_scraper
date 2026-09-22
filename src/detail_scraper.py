"""
Stage 2: visit each company's page and pull founder name/role/LinkedIn.

Plain `requests` gets blocked here at scraper volume (YC's anti-bot layer
flags the traffic pattern even though a single curl works fine), so this
stage drives a real, undetected Chrome via nodriver and hands the rendered
HTML to BeautifulSoup for extraction, nodriver does the fetch, bs4 does the
parsing, same as the original scraper.
"""
import asyncio
import random
from typing import Optional

import nodriver as uc
from bs4 import BeautifulSoup

from . import config
from .logger import get_logger
from .models import Company, Founder

log = get_logger(__name__)


class CompanyDetailScraper:
    """Async context manager: owns one browser instance, reused across every
    company so we're not paying Chrome startup cost per page."""

    def __init__(self, headless: bool = config.HEADLESS):
        self.headless = headless
        self._browser: Optional[uc.Browser] = None

    async def __aenter__(self) -> "CompanyDetailScraper":
        self._browser = await uc.start(headless=self.headless)
        return self

    async def __aexit__(self, *exc_info) -> None:
        if self._browser:
            self._browser.stop()

    async def scrape(self, slug: str, name: str, website: str) -> Company:
        company = Company(slug=slug, name=name, website=website)
        url = config.YC_COMPANY_DETAIL_URL.format(slug=slug)
        try:
            await self._browser.get(url)
            tab = self._browser.main_tab
            found = await tab.select("div.min-w-0.flex-1", timeout=10)
            if not found:
                log.warning("Founders section did not load for %s", slug)
            html = await tab.get_content()
            company.founders = self._parse_founders(html)
            if not company.founders:
                log.warning("No founders parsed for %s", slug)
        except Exception as exc:
            log.error("Failed to scrape %s: %s", slug, exc)
            company.scrape_error = str(exc)

        await asyncio.sleep(random.uniform(*config.REQUEST_DELAY_RANGE))
        return company

    @staticmethod
    def _parse_founders(html: str) -> list[Founder]:
        soup = BeautifulSoup(html, "html.parser")
        founders: list[Founder] = []
        seen: set[tuple[str, str]] = set()

        for block in soup.select("div.min-w-0.flex-1"):
            name_el = block.select_one("div.text-xl.font-bold")
            if not name_el:
                continue
            role_el = block.select_one("div.text-gray-600")
            linkedin_el = block.select_one('a[aria-label="LinkedIn profile"]')

            name = name_el.get_text(strip=True)
            linkedin = linkedin_el["href"] if linkedin_el else None

            key = (name, linkedin or "")
            if key in seen:  # site renders a duplicate mobile-layout copy
                continue
            seen.add(key)

            founders.append(
                Founder(
                    name=name,
                    role=role_el.get_text(strip=True) if role_el else "",
                    linkedin_url=linkedin,
                )
            )
        return founders
