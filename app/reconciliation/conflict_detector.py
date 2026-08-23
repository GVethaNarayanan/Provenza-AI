"""Provenza AI - Conflict Detector

Detects conflicts between attributes from different sources.
Handles numerical, categorical, and text comparisons with normalization.
"""

import logging
import re
import uuid
from typing import Optional

from app.models.source import ExtractedAttribute, SourceMetadata
from app.models.reconciliation import ConflictDetail
from app.normalization.unit_normalizer import extract_numeric, normalize_unit
from app.normalization.material_normalizer import normalize_value_by_attribute
from app.reconciliation.trust_scorer import TrustScorer

logger = logging.getLogger(__name__)


class ConflictDetector:
    """Detects and classifies conflicts between multi-source attributes."""

    def __init__(self, trust_scorer: Optional[TrustScorer] = None):
        self.trust_scorer = trust_scorer or TrustScorer()

    # Attributes considered numerical
    NUMERICAL_ATTRIBUTES = {
        "pressure_rating", "temperature_rating", "size", "weight",
        "flow_rate", "cv_value",
    }

    # Attributes considered categorical
    CATEGORICAL_ATTRIBUTES = {
        "material", "body_material", "seal_material", "connection_type",
        "bore_type", "category", "standard", "color",
    }

    def detect_conflict(
        self,
        attribute: str,
        attr_a: ExtractedAttribute,
        attr_b: ExtractedAttribute,
        source_a: SourceMetadata,
        source_b: SourceMetadata,
    ) -> Optional[ConflictDetail]:
        """
        Compare two attribute values and detect conflicts.

        Returns ConflictDetail if conflict detected, None if values match.
        """
        val_a = attr_a.value
        val_b = attr_b.value

        if val_a is None or val_b is None:
            return None  # One source missing → enrichment, not conflict

        # Determine comparison type
        if attribute in self.NUMERICAL_ATTRIBUTES:
            is_conflict = self._compare_numerical(val_a, val_b, attr_a.unit, attr_b.unit)
        elif attribute in self.CATEGORICAL_ATTRIBUTES:
            is_conflict = self._compare_categorical(attribute, val_a, val_b)
        else:
            is_conflict = self._compare_text(val_a, val_b)

        if not is_conflict:
            return None

        # Conflict detected — calculate trust comparison
        trust_result = self.trust_scorer.compare_source_trust(
            attr_a, source_a, attr_b, source_b
        )

        conflict = ConflictDetail(
            conflict_id=f"CNF-{str(uuid.uuid4())[:6].upper()}",
            attribute=attribute,
            display_name=attr_a.display_name or attr_b.display_name or attribute.replace('_', ' ').title(),
            source_a_value=val_a,
            source_a_unit=attr_a.unit,
            source_a_name=source_a.source_name,
            source_a_id=source_a.source_id,
            source_a_reliability=self.trust_scorer.get_reliability_label(
                trust_result["trust_a"]["final_confidence"]
            ),
            source_a_reliability_score=trust_result["trust_a"]["final_confidence"],
            source_a_evidence=(
                attr_a.evidence.text_snippet if attr_a.evidence else ""
            ),
            source_b_value=val_b,
            source_b_unit=attr_b.unit,
            source_b_name=source_b.source_name,
            source_b_id=source_b.source_id,
            source_b_reliability=self.trust_scorer.get_reliability_label(
                trust_result["trust_b"]["final_confidence"]
            ),
            source_b_reliability_score=trust_result["trust_b"]["final_confidence"],
            source_b_evidence=(
                attr_b.evidence.text_snippet if attr_b.evidence else ""
            ),
            recommendation=trust_result["recommended_value"],
            recommendation_unit=trust_result["recommended_unit"],
            recommendation_source=trust_result["recommended_source"],
            confidence=trust_result["confidence"],
            reasoning=trust_result["reasoning"],
            review_status="requires_review" if trust_result["requires_review"] else "auto_resolved",
        )

        return conflict

    def _compare_numerical(
        self, val_a: str, val_b: str,
        unit_a: Optional[str], unit_b: Optional[str]
    ) -> bool:
        """Compare numerical values after unit normalization."""
        # Normalize units
        norm_unit_a = normalize_unit(unit_a) if unit_a else None
        norm_unit_b = normalize_unit(unit_b) if unit_b else None

        # Extract numeric values
        num_a = extract_numeric(val_a)
        num_b = extract_numeric(val_b)

        if num_a is None or num_b is None:
            # Can't parse as numbers → fallback to text comparison
            return self._compare_text(val_a, val_b)

        # If units differ and are not convertible, it's a conflict
        if norm_unit_a and norm_unit_b and norm_unit_a != norm_unit_b:
            return True

        # Compare numeric values with tolerance
        if num_a == 0 and num_b == 0:
            return False
        tolerance = max(abs(num_a), abs(num_b)) * 0.01  # 1% tolerance
        return abs(num_a - num_b) > tolerance

    def _compare_categorical(self, attribute: str, val_a: str, val_b: str) -> bool:
        """Compare categorical values after normalization."""
        norm_a = normalize_value_by_attribute(attribute, val_a).lower().strip()
        norm_b = normalize_value_by_attribute(attribute, val_b).lower().strip()

        if norm_a == norm_b:
            return False

        # Check if one is a more specific version of the other
        # e.g., "Stainless Steel" vs "304 Stainless Steel" → NOT a conflict (enrichment)
        if norm_a in norm_b or norm_b in norm_a:
            return False

        return True

    def _compare_text(self, val_a: str, val_b: str) -> bool:
        """Compare text values with tolerance for abbreviations and overlap."""
        norm_a = val_a.lower().strip()
        norm_b = val_b.lower().strip()

        if norm_a == norm_b:
            return False

        # Check containment (one is a superset of the other)
        if norm_a in norm_b or norm_b in norm_a:
            return False

        # Expand common abbreviations before comparing
        abbreviations = {
            "ss": "stainless steel",
            "cs": "carbon steel",
            "ci": "cast iron",
        }
        expanded_a = norm_a
        expanded_b = norm_b
        for abbr, full in abbreviations.items():
            expanded_a = re.sub(r'\b' + abbr + r'\b', full, expanded_a)
            expanded_b = re.sub(r'\b' + abbr + r'\b', full, expanded_b)

        if expanded_a == expanded_b:
            return False
        if expanded_a in expanded_b or expanded_b in expanded_a:
            return False

        # Word overlap check — if most words match, not a conflict
        words_a = set(expanded_a.split())
        words_b = set(expanded_b.split())
        if words_a and words_b:
            overlap = len(words_a & words_b)
            total = max(len(words_a), len(words_b))
            if total > 0 and overlap / total >= 0.6:
                return False

        return True
