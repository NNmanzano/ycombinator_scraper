# YCombinator Scraper

Pulls the public YC company directory (name, website, CEO, CEO LinkedIn) into
a single Excel file, one row per company. Built as a pipeline that keeps working when a page fails to load or the
site's anti-bot layer flags a request.

## Highlights

- Company detail pages are rendered with `nodriver` (real, undetected Chrome),
  not raw `requests`. YC blocks plain HTTP clients at scraper volume, a real
  browser session does not get flagged.
- The Algolia search key that powers YC's company list is resolved live off
  the public companies page on every run, so the
  scraper does not silently die the next time YC rotates it.
- Each company scrapes independently. One broken page (layout glitch, network
  blip) gets logged and skipped, it does not take down a 150+ company run.
- Every run writes to `logs/scraper.log` in addition to the console, and any
  company that failed to parse is listed in `data/failed_slugs.json` for a
  quick re-run or manual check.

## Directory layout

```
ycombinator_v2/
├── main.py              entry point / CLI, run this
├── requirements.txt
├── src/
│   ├── config.py         all URLs, paths, batches, timing knobs, edit here, nowhere else
│   ├── logger.py          logging setup (console + logs/scraper.log)
│   ├── models.py          Company / Founder dataclasses + row shaping for Excel
│   ├── algolia_client.py  Stage 1, fetch the company list (requests, plain JSON API)
│   ├── detail_scraper.py  Stage 2, nodriver renders each company page, bs4 parses founders
│   ├── exporter.py        Stage 3, writes data/companies.xlsx
│   └── pipeline.py         wires the 3 stages together, tracks per-company failures
├── data/                 output: companies_raw.json, companies.xlsx, failed_slugs.json (gitignored)
├── logs/                 scraper.log (gitignored)
└── venv/                 (gitignored)
```

Looking for something specific:
- Change which batches get scraped: `src/config.py` (`DEFAULT_BATCHES`) or `--batches` flag.
- Change how a founder's name/LinkedIn is parsed: `src/detail_scraper.py::_parse_founders`.
- Change the Excel columns: `src/models.py::Company.to_row`.
- Change output paths: `src/config.py`.

## Setup

```
python -m venv venv
venv\Scripts\pip install -r requirements.txt
```

Requires Google Chrome (or Chromium/Edge/Brave) installed locally, nodriver
drives it directly, no chromedriver/Selenium involved.

## Run

```
venv\Scripts\python main.py --batches "Winter 2025" --limit 10
```

- `--batches`: one or more YC batch names, e.g. `"Winter 2025" "Summer 2025"`.
- `--limit N`: only scrape the first N companies (useful for a quick smoke test).
- `--show-browser`: run Chrome visibly instead of headless, for debugging.

Output: `data/companies.xlsx`. Progress and errors go to the console and
`logs/scraper.log`. Companies whose detail page failed to parse are listed
in `data/failed_slugs.json`.
