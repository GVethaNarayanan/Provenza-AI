"""Provenza AI - PDF Parser

Uses pdfplumber (primary) + PyMuPDF (fallback) for text and table extraction.
Falls back to OCR (pytesseract) for scanned/image-based PDFs.
"""

import logging
from pathlib import Path
from app.ingestion.base import BaseParser
from app.models.source import ParsedDocument, ParsedPage

logger = logging.getLogger(__name__)


class PDFParser(BaseParser):
    """PDF document parser with multi-strategy extraction."""

    def can_parse(self, file_path: str) -> bool:
        return Path(file_path).suffix.lower() == ".pdf"

    def parse(self, file_path: str, source_id: str, source_name: str) -> ParsedDocument:
        """Parse PDF using pdfplumber → PyMuPDF → OCR fallback chain."""
        if not Path(file_path).exists():
            return ParsedDocument(
                source_id=source_id,
                source_name=source_name,
                parse_success=False,
                error_message=f"File not found: {file_path}",
            )

        # Try pdfplumber first (best for tables + text)
        doc = self._parse_with_pdfplumber(file_path, source_id, source_name)
        if doc.parse_success and doc.full_text.strip():
            doc.parse_method = "pdfplumber"
            return doc

        # Fallback to PyMuPDF
        logger.info(f"pdfplumber failed or empty, trying PyMuPDF for {file_path}")
        doc = self._parse_with_pymupdf(file_path, source_id, source_name)
        if doc.parse_success and doc.full_text.strip():
            doc.parse_method = "pymupdf"
            return doc

        # OCR fallback
        logger.info(f"Text extraction failed, trying OCR for {file_path}")
        doc = self._parse_with_ocr(file_path, source_id, source_name)
        if doc.parse_success:
            doc.parse_method = "ocr"
        return doc

    def _parse_with_pdfplumber(self, file_path: str, source_id: str, source_name: str) -> ParsedDocument:
        """Extract text and tables using pdfplumber."""
        try:
            import pdfplumber

            pages = []
            all_text = []

            with pdfplumber.open(file_path) as pdf:
                for i, page in enumerate(pdf.pages):
                    text = page.extract_text() or ""
                    tables = []

                    # Extract tables
                    page_tables = page.extract_tables()
                    if page_tables:
                        for table in page_tables:
                            cleaned_table = [
                                [str(cell) if cell else "" for cell in row]
                                for row in table if row
                            ]
                            if cleaned_table:
                                tables.append(cleaned_table)

                    pages.append(ParsedPage(
                        page_number=i + 1,
                        text_content=text,
                        tables=tables,
                    ))
                    all_text.append(text)

                return ParsedDocument(
                    source_id=source_id,
                    source_name=source_name,
                    pages=pages,
                    full_text="\n\n".join(all_text),
                    total_pages=len(pdf.pages),
                    parse_success=True,
                )

        except Exception as e:
            logger.warning(f"pdfplumber failed: {e}")
            return ParsedDocument(
                source_id=source_id,
                source_name=source_name,
                parse_success=False,
                error_message=str(e),
            )

    def _parse_with_pymupdf(self, file_path: str, source_id: str, source_name: str) -> ParsedDocument:
        """Extract text using PyMuPDF (fitz)."""
        try:
            import fitz  # PyMuPDF

            pages = []
            all_text = []

            doc = fitz.open(file_path)
            for i, page in enumerate(doc):
                text = page.get_text("text") or ""
                pages.append(ParsedPage(
                    page_number=i + 1,
                    text_content=text,
                ))
                all_text.append(text)

            result = ParsedDocument(
                source_id=source_id,
                source_name=source_name,
                pages=pages,
                full_text="\n\n".join(all_text),
                total_pages=len(doc),
                parse_success=True,
            )
            doc.close()
            return result

        except Exception as e:
            logger.warning(f"PyMuPDF failed: {e}")
            return ParsedDocument(
                source_id=source_id,
                source_name=source_name,
                parse_success=False,
                error_message=str(e),
            )

    def _parse_with_ocr(self, file_path: str, source_id: str, source_name: str) -> ParsedDocument:
        """Extract text using OCR (pytesseract + PyMuPDF for image rendering)."""
        try:
            import fitz  # PyMuPDF
            from PIL import Image
            import pytesseract
            import io

            pages = []
            all_text = []

            doc = fitz.open(file_path)
            for i, page in enumerate(doc):
                # Render page to image
                mat = fitz.Matrix(2.0, 2.0)  # 2x zoom for better OCR
                pix = page.get_pixmap(matrix=mat)
                img_data = pix.tobytes("png")
                img = Image.open(io.BytesIO(img_data))

                # OCR
                text = pytesseract.image_to_string(img) or ""
                pages.append(ParsedPage(
                    page_number=i + 1,
                    text_content=text,
                ))
                all_text.append(text)

            result = ParsedDocument(
                source_id=source_id,
                source_name=source_name,
                pages=pages,
                full_text="\n\n".join(all_text),
                total_pages=len(doc),
                parse_success=True,
            )
            doc.close()
            return result

        except ImportError:
            logger.warning("pytesseract not available for OCR fallback")
            return ParsedDocument(
                source_id=source_id,
                source_name=source_name,
                parse_success=False,
                error_message="OCR not available (pytesseract not installed)",
            )
        except Exception as e:
            logger.warning(f"OCR failed: {e}")
            return ParsedDocument(
                source_id=source_id,
                source_name=source_name,
                parse_success=False,
                error_message=str(e),
            )
