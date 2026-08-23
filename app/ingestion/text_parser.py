"""Provenza AI - Text File Parser"""

import logging
from pathlib import Path
from app.ingestion.base import BaseParser
from app.models.source import ParsedDocument, ParsedPage

logger = logging.getLogger(__name__)


class TextParser(BaseParser):
    """Plain text file parser."""

    def can_parse(self, file_path: str) -> bool:
        return Path(file_path).suffix.lower() == ".txt"

    def parse(self, file_path: str, source_id: str, source_name: str) -> ParsedDocument:
        try:
            text = Path(file_path).read_text(encoding="utf-8")
            return ParsedDocument(
                source_id=source_id,
                source_name=source_name,
                pages=[ParsedPage(page_number=1, text_content=text)],
                full_text=text,
                total_pages=1,
                parse_method="text",
                parse_success=True,
            )
        except Exception as e:
            logger.error(f"Text parse failed: {e}")
            return ParsedDocument(
                source_id=source_id,
                source_name=source_name,
                parse_success=False,
                error_message=str(e),
            )
