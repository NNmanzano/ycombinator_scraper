"""
Stage 3: write the scraped companies to an .xlsx file.
"""
import pandas as pd

from . import config
from .logger import get_logger
from .models import Company

log = get_logger(__name__)


class ExcelExporter:
    @staticmethod
    def export(companies: list[Company], path=config.EXCEL_OUTPUT) -> None:
        config.DATA_DIR.mkdir(parents=True, exist_ok=True)
        df = pd.DataFrame([c.to_row() for c in companies])
        df.to_excel(path, index=False)
        log.info("Wrote %d rows to %s", len(companies), path)
