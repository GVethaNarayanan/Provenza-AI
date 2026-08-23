"""Provenza AI - Trust Scoring & Conflict Detection Tests"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from datetime import datetime
from app.reconciliation.trust_scorer import TrustScorer
from app.reconciliation.conflict_detector import ConflictDetector
from app.models.source import (
    SourceMetadata, SourceType, SourceAuthority,
    ExtractedAttribute, ExtractedEvidence,
)


def make_attr(value, unit=None, confidence=0.9, evidence_text="", source_name="Test"):
    """Helper to create test attributes."""
    return ExtractedAttribute(
        attribute="test",
        display_name="Test",
        value=value,
        unit=unit,
        extraction_confidence=confidence,
        source_id="test",
        source_name=source_name,
        evidence=ExtractedEvidence(
            text_snippet=evidence_text,
            source_id="test",
            source_name=source_name,
        ) if evidence_text else None,
    )


def make_source(name, authority, recency_date=None):
    """Helper to create test source metadata."""
    return SourceMetadata(
        source_name=name,
        source_type=SourceType.PDF,
        authority=authority,
        recency_date=recency_date or datetime.now(),
    )


class TestTrustScorer:
    """Tests for the trust scoring engine."""

    def test_basic_scoring(self):
        scorer = TrustScorer()
        attr = make_attr("200", "PSI", confidence=0.95, evidence_text="Pressure: 200 PSI")
        source = make_source("Tech Spec", SourceAuthority.VERY_HIGH)

        result = scorer.calculate_field_confidence(attr, source)
        assert "final_confidence" in result
        assert 0.0 <= result["final_confidence"] <= 1.0
        assert "breakdown" in result

    def test_high_authority_scores_higher(self):
        scorer = TrustScorer()
        attr = make_attr("200", "PSI", confidence=0.9, evidence_text="200 PSI")

        source_high = make_source("Tech Spec", SourceAuthority.VERY_HIGH)
        source_low = make_source("Third Party", SourceAuthority.LOW)

        score_high = scorer.calculate_field_confidence(attr, source_high)
        score_low = scorer.calculate_field_confidence(attr, source_low)

        assert score_high["final_confidence"] > score_low["final_confidence"]

    def test_recent_source_scores_higher(self):
        scorer = TrustScorer()
        attr = make_attr("200", "PSI", confidence=0.9)

        source_new = make_source("New", SourceAuthority.MEDIUM, datetime(2026, 6, 1))
        source_old = make_source("Old", SourceAuthority.MEDIUM, datetime(2020, 1, 1))

        score_new = scorer.calculate_field_confidence(attr, source_new)
        score_old = scorer.calculate_field_confidence(attr, source_old)

        assert score_new["final_confidence"] > score_old["final_confidence"]

    def test_trust_comparison(self):
        scorer = TrustScorer()
        attr_a = make_attr("150", "PSI", confidence=0.93, evidence_text="150 PSI")
        attr_b = make_attr("200", "PSI", confidence=0.97, evidence_text="Pressure Rating: 200 PSI")

        source_a = make_source("Old Catalog", SourceAuthority.MEDIUM, datetime(2023, 3, 15))
        source_b = make_source("New Spec", SourceAuthority.VERY_HIGH, datetime(2026, 6, 1))

        result = scorer.compare_source_trust(attr_a, source_a, attr_b, source_b)

        assert result["recommended_value"] == "200"
        assert result["confidence"] > 0.0
        assert "reasoning" in result

    def test_reliability_labels(self):
        scorer = TrustScorer()
        assert scorer.get_reliability_label(0.95) == "Very High"
        assert scorer.get_reliability_label(0.85) == "High"
        assert scorer.get_reliability_label(0.60) == "Medium"
        assert scorer.get_reliability_label(0.30) == "Very Low"

    def test_custom_weights(self):
        weights = {
            "source_authority": 0.50,
            "recency": 0.20,
            "evidence_quality": 0.15,
            "extraction_confidence": 0.10,
            "cross_source_agreement": 0.05,
        }
        scorer = TrustScorer(weights=weights)
        attr = make_attr("200", confidence=0.9)
        source = make_source("Test", SourceAuthority.VERY_HIGH)

        result = scorer.calculate_field_confidence(attr, source)
        assert result["final_confidence"] > 0.0


class TestConflictDetection:
    """Tests for conflict detection."""

    def test_numerical_conflict(self):
        detector = ConflictDetector()
        attr_a = make_attr("150", "PSI", confidence=0.93, evidence_text="150 PSI")
        attr_b = make_attr("200", "PSI", confidence=0.97, evidence_text="200 PSI")

        source_a = make_source("Old", SourceAuthority.MEDIUM)
        source_b = make_source("New", SourceAuthority.VERY_HIGH)

        conflict = detector.detect_conflict("pressure_rating", attr_a, attr_b, source_a, source_b)

        assert conflict is not None
        assert conflict.source_a_value == "150"
        assert conflict.source_b_value == "200"
        assert conflict.recommendation is not None
        assert conflict.confidence > 0.0

    def test_no_conflict_matching_values(self):
        detector = ConflictDetector()
        attr_a = make_attr("200", "PSI")
        attr_b = make_attr("200", "PSI")

        source_a = make_source("A", SourceAuthority.MEDIUM)
        source_b = make_source("B", SourceAuthority.HIGH)

        conflict = detector.detect_conflict("pressure_rating", attr_a, attr_b, source_a, source_b)
        assert conflict is None

    def test_categorical_no_conflict_enrichment(self):
        """'Stainless Steel' vs '304 Stainless Steel' should NOT be a conflict (enrichment)."""
        detector = ConflictDetector()
        attr_a = make_attr("Stainless Steel")
        attr_b = make_attr("304 Stainless Steel")

        source_a = make_source("A", SourceAuthority.MEDIUM)
        source_b = make_source("B", SourceAuthority.HIGH)

        conflict = detector.detect_conflict("material", attr_a, attr_b, source_a, source_b)
        # After normalization, "Stainless Steel" is contained in "304 Stainless Steel"
        assert conflict is None

    def test_categorical_conflict(self):
        detector = ConflictDetector()
        attr_a = make_attr("Carbon Steel")
        attr_b = make_attr("304 Stainless Steel")

        source_a = make_source("A", SourceAuthority.MEDIUM)
        source_b = make_source("B", SourceAuthority.HIGH)

        conflict = detector.detect_conflict("material", attr_a, attr_b, source_a, source_b)
        assert conflict is not None

    def test_null_value_no_conflict(self):
        detector = ConflictDetector()
        attr_a = make_attr("200", "PSI")
        attr_b = make_attr(None)

        source_a = make_source("A", SourceAuthority.MEDIUM)
        source_b = make_source("B", SourceAuthority.HIGH)

        conflict = detector.detect_conflict("pressure_rating", attr_a, attr_b, source_a, source_b)
        assert conflict is None  # Missing = enrichment opportunity


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
