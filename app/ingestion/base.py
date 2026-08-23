"""Provenza AI - Base Parser Interface"""

from abc import ABC, abstractmethod
from app.models.source import ParsedDocument


class BaseParser(ABC):
    """Abstract base class for document parsers."""

    @abstractmethod
    def parse(self, file_path: str, source_id: str, source_name: str) -> ParsedDocument:
        """Parse a document and return structured content."""
        pass

    @abstractmethod
    def can_parse(self, file_path: str) -> bool:
        """Check if this parser can handle the given file."""
        pass
