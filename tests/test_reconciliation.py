"""Provenza AI - Reconciliation Engine Integration Test

Tests the complete reconciliation pipeline using the demo data.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from app.demo.demo_data import (
    get_demo_attrs_a, get_demo_attrs_b,
    DEMO_SOURCE_A, DEMO_SOURCE_B, DEMO_PRODUCT_INPUT
)
from app.reconciliation.engine import ReconciliationEngine
from app.models.reconciliation import AttributeStatus
from app.models.audit import AuditTrail


class TestReconciliationEngine:
    """Integration tests for the reconciliation engine."""

    def setup_method(self):
        self.engine = ReconciliationEngine()
        self.attrs_a = get_demo_attrs_a()
        self.attrs_b = get_demo_attrs_b()

    def test_reconciliation_runs(self):
        """Test that reconciliation produces results."""
        result = self.engine.reconcile(
            self.attrs_a, self.attrs_b,
            DEMO_SOURCE_A, DEMO_SOURCE_B,
            product_id="TEST-001",
        )
        assert result is not None
        assert result.total_attributes > 0

    def test_pressure_conflict_detected(self):
        """Test that the pressure rating conflict is detected."""
        result = self.engine.reconcile(
            self.attrs_a, self.attrs_b,
            DEMO_SOURCE_A, DEMO_SOURCE_B,
        )

        # Find pressure conflict
        pressure_conflicts = [
            c for c in result.conflicts
            if c.attribute == "pressure_rating"
        ]
        assert len(pressure_conflicts) == 1

        conflict = pressure_conflicts[0]
        assert conflict.source_a_value == "150"
        assert conflict.source_b_value == "200"
        assert conflict.recommendation is not None

    def test_size_matches(self):
        """Test that matching sizes are classified as MATCH."""
        result = self.engine.reconcile(
            self.attrs_a, self.attrs_b,
            DEMO_SOURCE_A, DEMO_SOURCE_B,
        )

        size_entries = [e for e in result.entries if e.attribute == "size"]
        assert len(size_entries) == 1
        assert size_entries[0].status == AttributeStatus.MATCH

    def test_enriched_attributes(self):
        """Test that attributes only in Source B are ENRICHED."""
        result = self.engine.reconcile(
            self.attrs_a, self.attrs_b,
            DEMO_SOURCE_A, DEMO_SOURCE_B,
        )

        enriched = [e for e in result.entries if e.status == AttributeStatus.ENRICHED]
        enriched_names = [e.attribute for e in enriched]

        # Connection type should be enriched (only in Source B)
        assert "connection_type" in enriched_names

    def test_product_record_generation(self):
        """Test that a complete product record is generated."""
        result = self.engine.reconcile(
            self.attrs_a, self.attrs_b,
            DEMO_SOURCE_A, DEMO_SOURCE_B,
            product_id="TEST-001",
        )

        audit = AuditTrail(product_id="TEST-001")
        record = self.engine.build_product_record(
            reconciliation=result,
            product_input={
                "product_id": "TEST-001",
                "product_name": "Test Valve",
                "brand": "TestBrand",
                "category": "Ball Valve",
                "model_number": "SS-304-V2",
            },
            source_a=DEMO_SOURCE_A,
            source_b=DEMO_SOURCE_B,
            audit_trail=audit,
        )

        assert record.product_id == "TEST-001"
        assert len(record.attributes) > 0
        assert record.overall_confidence > 0.0
        assert len(record.sources) == 2

    def test_commerce_dict_export(self):
        """Test that the commerce-ready dict contains all required fields."""
        result = self.engine.reconcile(
            self.attrs_a, self.attrs_b,
            DEMO_SOURCE_A, DEMO_SOURCE_B,
        )

        record = self.engine.build_product_record(
            reconciliation=result,
            product_input={
                "product_id": "TEST-001",
                "product_name": "Test Valve",
                "brand": "TestBrand",
                "category": "Ball Valve",
                "model_number": "SS-304-V2",
            },
            source_a=DEMO_SOURCE_A,
            source_b=DEMO_SOURCE_B,
        )

        commerce = record.to_commerce_dict()
        assert "product_id" in commerce
        assert "attributes" in commerce
        assert "overall_confidence" in commerce
        assert "sources" in commerce
        assert "conflicts" in commerce

    def test_has_both_matches_and_conflicts(self):
        """The demo data should produce both matches and conflicts."""
        result = self.engine.reconcile(
            self.attrs_a, self.attrs_b,
            DEMO_SOURCE_A, DEMO_SOURCE_B,
        )

        assert result.matched_count > 0, "Should have matched attributes"
        assert result.conflict_count > 0, "Should have conflicts (pressure)"
        assert result.enriched_count > 0, "Should have enriched attributes"

    def test_conflict_recommendation_is_source_b(self):
        """For pressure conflict, Source B (new spec, very high authority) should be recommended."""
        result = self.engine.reconcile(
            self.attrs_a, self.attrs_b,
            DEMO_SOURCE_A, DEMO_SOURCE_B,
        )

        pressure_conflict = next(
            c for c in result.conflicts if c.attribute == "pressure_rating"
        )

        # Source B has higher authority (VERY_HIGH vs MEDIUM) and is more recent
        assert pressure_conflict.recommendation == "200"
        assert pressure_conflict.confidence > 0.80

    def test_audit_trail_populated(self):
        """Test that audit trail entries are created during reconciliation."""
        result = self.engine.reconcile(
            self.attrs_a, self.attrs_b,
            DEMO_SOURCE_A, DEMO_SOURCE_B,
        )

        audit = AuditTrail(product_id="TEST-001")
        self.engine.build_product_record(
            reconciliation=result,
            product_input={"product_id": "TEST-001", "product_name": "Test"},
            source_a=DEMO_SOURCE_A,
            source_b=DEMO_SOURCE_B,
            audit_trail=audit,
        )

        assert len(audit.entries) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
