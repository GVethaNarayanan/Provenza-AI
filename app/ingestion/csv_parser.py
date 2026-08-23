"""Provenza AI - CSV/XLSX Parser"""

import logging
from pathlib import Path
from app.ingestion.base import BaseParser
from app.models.source import ParsedDocument, ParsedPage

logger = logging.getLogger(__name__)


class CSVParser(BaseParser):
    """CSV and XLSX file parser."""

    SUPPORTED_EXTENSIONS = {".csv", ".xlsx", ".xls"}

    def can_parse(self, file_path: str) -> bool:
        return Path(file_path).suffix.lower() in self.SUPPORTED_EXTENSIONS

    def parse(self, file_path: str, source_id: str, source_name: str) -> ParsedDocument:
        ext = Path(file_path).suffix.lower()
        try:
            import pandas as pd

            if ext == ".csv":
                df = pd.read_csv(file_path)
            else:
                df = pd.read_excel(file_path)

            # Convert to key-value line representation and CSV text
            kv_lines = []
            if len(df) > 0:
                first_row = df.iloc[0]
                for col in df.columns:
                    val = str(first_row[col]).strip()
                    if val and val.lower() != "nan":
                        kv_lines.append(f"{col}: {val}")

            text = "\n".join(kv_lines) if kv_lines else df.to_string(index=False)

            # Convert to table format
            headers = df.columns.tolist()
            rows = df.astype(str).values.tolist()
            table = [headers] + rows

            return ParsedDocument(
                source_id=source_id,
                source_name=source_name,
                pages=[ParsedPage(
                    page_number=1,
                    text_content=text,
                    tables=[table],
                )],
                full_text=text,
                total_pages=1,
                parse_method="pandas",
                parse_success=True,
                metadata={"columns": headers, "rows": len(df)},
            )
        except Exception as e:
            logger.error(f"CSV/XLSX parse failed: {e}")
            return ParsedDocument(
                source_id=source_id,
                source_name=source_name,
                parse_success=False,
                error_message=str(e),
            )
