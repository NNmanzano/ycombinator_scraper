"""
All paths, URLs and tunable knobs in one place. Nothing here is behavior,
just values, if you need to point the scraper at different batches or
output locations, this is the only file to touch.
"""
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
LOG_DIR = BASE_DIR / "logs"

RAW_COMPANIES_JSON = DATA_DIR / "companies_raw.json"
EXCEL_OUTPUT = DATA_DIR / "companies.xlsx"
FAILED_SLUGS_JSON = DATA_DIR / "failed_slugs.json"

YC_COMPANIES_PAGE = "https://www.ycombinator.com/companies"
YC_COMPANY_DETAIL_URL = "https://www.ycombinator.com/companies/{slug}"

ALGOLIA_SEARCH_URL = "https://45bwzj1sgc-dsn.algolia.net/1/indexes/*/queries"
ALGOLIA_INDEX = "YCCompany_production"
ALGOLIA_APP_ID = "45BWZJ1SGC"
# YC rotates this public search key periodically. AlgoliaCompanyListClient
# scrapes the live key from YC_COMPANIES_PAGE first; this is only the last-resort
# fallback if that scrape ever fails.
ALGOLIA_API_KEY_FALLBACK = (
    "NzJmMWExZWYxYzY5OGYwN2VkYWM5YzRiM2VlNDFlM2I0ODU2YjQ2Yjg0MTFiNWE5NzY0NTMyZGI1"
    "OWEwMzVjY2FuYWx5dGljc1RhZ3M9eWNkYyZyZXN0cmljdEluZGljZXM9WUNDb21wYW55X3Byb2R1"
    "Y3Rpb24lMkNZQ0NvbXBhbnlfQnlfTGF1bmNoX0RhdGVfcHJvZHVjdGlvbiZ0YWdGaWx0ZXJzPSU1"
    "QiUyMnljZGNfcHVibGljJTIyJTVE"
)

DEFAULT_BATCHES = ["Winter 2025"]

HEADLESS = True
REQUEST_DELAY_RANGE = (1.0, 3.0)  # polite delay between company detail pages

