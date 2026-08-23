"""Provenza AI - In-Memory Store

MongoDB-compatible interface for hackathon MVP.
Data shapes are designed for easy MongoDB migration post-hackathon.
"""

import logging
from typing import Optional

from app.models.product import ProductRecord
from app.models.audit import AuditTrail, AuditEntry
from app.models.reconciliation import ReconciliationResult

logger = logging.getLogger(__name__)


class Store:
    """In-memory data store with MongoDB-ready interface."""

    def __init__(self):
        self._products: dict[str, ProductRecord] = {}
        self._audit_trails: dict[str, AuditTrail] = {}
        self._reconciliations: dict[str, ReconciliationResult] = {}
        self._sources: dict[str, dict] = {}

    # ── Products ──────────────────────────────────────────

    def save_product(self, product: ProductRecord) -> None:
        self._products[product.product_id] = product
        logger.info(f"Saved product: {product.product_id}")

    def get_product(self, product_id: str) -> Optional[ProductRecord]:
        return self._products.get(product_id)

    def list_products(self) -> list[ProductRecord]:
        return list(self._products.values())

    def delete_product(self, product_id: str) -> bool:
        if product_id in self._products:
            del self._products[product_id]
            return True
        return False

    # ── Audit Trails ──────────────────────────────────────

    def get_or_create_audit_trail(self, product_id: str) -> AuditTrail:
        if product_id not in self._audit_trails:
            self._audit_trails[product_id] = AuditTrail(product_id=product_id)
        return self._audit_trails[product_id]

    def add_audit_entry(self, product_id: str, **kwargs) -> AuditEntry:
        trail = self.get_or_create_audit_trail(product_id)
        return trail.add_entry(**kwargs)

    def get_audit_trail(self, product_id: str) -> Optional[AuditTrail]:
        return self._audit_trails.get(product_id)

    def get_all_audit_entries(self) -> list[AuditEntry]:
        entries = []
        for trail in self._audit_trails.values():
            entries.extend(trail.entries)
        return sorted(entries, key=lambda e: e.timestamp, reverse=True)

    # ── Reconciliations ───────────────────────────────────

    def save_reconciliation(self, result: ReconciliationResult) -> None:
        self._reconciliations[result.product_id] = result

    def get_reconciliation(self, product_id: str) -> Optional[ReconciliationResult]:
        return self._reconciliations.get(product_id)

    # ── Sources ───────────────────────────────────────────

    def save_source(self, source_id: str, source_data: dict) -> None:
        self._sources[source_id] = source_data

    def get_source(self, source_id: str) -> Optional[dict]:
        return self._sources.get(source_id)

    # ── Stats ─────────────────────────────────────────────

    def get_stats(self) -> dict:
        total_attributes = 0
        total_conflicts = 0
        total_validated = 0
        total_review = 0

        for product in self._products.values():
            total_attributes += len(product.attributes)
            total_conflicts += len(product.conflicts)
            for attr in product.attributes.values():
                if attr.status in ("validated", "provisionally_validated", "reviewed"):
                    total_validated += 1
                if attr.review_required:
                    total_review += 1

        return {
            "products_analyzed": len(self._products),
            "attributes_extracted": total_attributes,
            "conflicts_detected": total_conflicts,
            "attributes_validated": total_validated,
            "fields_requiring_review": total_review,
        }

    def clear(self) -> None:
        """Clear all data."""
        self._products.clear()
        self._audit_trails.clear()
        self._reconciliations.clear()
        self._sources.clear()


# Global store instance
store = Store()
