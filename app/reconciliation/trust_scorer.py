"""Provenza AI - Trust-Weighted Validation

Deterministic trust scoring system that does NOT let the LLM arbitrarily decide truth.
Configurable source priority with transparent scoring logic.
"""

import logging
from datetime import datetime
from typing import Optional

from app.config import TRUST_WEIGHTS, CONFIDENCE_THRESHOLD
from app.models.source import SourceMetadata, ExtractedAttribute

logger = logging.getLogger(__name__)


class TrustScorer:
    """Deterministic, transparent trust scoring engine."""

    def __init__(self, weights: Optional[dict] = None):
        self.weights = weights or TRUST_WEIGHTS.copy()
        # Normalize weights to sum to 1.0
        total = sum(self.weights.values())
        if total > 0:
            self.weights = {k: v / total for k, v in self.weights.items()}

    def calculate_field_confidence(
        self,
        attribute: ExtractedAttribute,
        source: SourceMetadata,
        cross_source_agreement: float = 0.5,
    ) -> dict:
        """
        Calculate field-level confidence using weighted combination.

        Returns dict with breakdown and final score.
        """
        # 1. Source Authority (from source metadata)
        authority_score = source.authority_score

        # 2. Recency (from source date)
        recency_score = source.recency_score

        # 3. Evidence Quality (from evidence text presence and specificity)
        evidence_score = self._evaluate_evidence_quality(attribute)

        # 4. Extraction Confidence (from LLM extraction)
        extraction_score = attribute.extraction_confidence

        # 5. Cross-Source Agreement (from reconciliation)
        agreement_score = cross_source_agreement

        # Weighted combination
        final_confidence = (
            self.weights["source_authority"] * authority_score +
            self.weights["recency"] * recency_score +
            self.weights["evidence_quality"] * evidence_score +
            self.weights["extraction_confidence"] * extraction_score +
            self.weights["cross_source_agreement"] * agreement_score
        )

        return {
            "final_confidence": round(min(final_confidence, 1.0), 4),
            "breakdown": {
                "source_authority": {
                    "score": round(authority_score, 4),
                    "weight": round(self.weights["source_authority"], 4),
                    "label": source.authority_label,
                },
                "recency": {
                    "score": round(recency_score, 4),
                    "weight": round(self.weights["recency"], 4),
                },
                "evidence_quality": {
                    "score": round(evidence_score, 4),
                    "weight": round(self.weights["evidence_quality"], 4),
                },
                "extraction_confidence": {
                    "score": round(extraction_score, 4),
                    "weight": round(self.weights["extraction_confidence"], 4),
                },
                "cross_source_agreement": {
                    "score": round(agreement_score, 4),
                    "weight": round(self.weights["cross_source_agreement"], 4),
                },
            },
            "requires_review": final_confidence < CONFIDENCE_THRESHOLD,
        }

    def compare_source_trust(
        self,
        attr_a: ExtractedAttribute,
        source_a: SourceMetadata,
        attr_b: ExtractedAttribute,
        source_b: SourceMetadata,
    ) -> dict:
        """
        Compare trust between two conflicting sources.

        Returns recommendation with confidence and reasoning.
        """
        trust_a = self.calculate_field_confidence(attr_a, source_a, cross_source_agreement=0.0)
        trust_b = self.calculate_field_confidence(attr_b, source_b, cross_source_agreement=0.0)

        conf_a = trust_a["final_confidence"]
        conf_b = trust_b["final_confidence"]

        # Determine recommendation
        if conf_b > conf_a:
            recommended_value = attr_b.value
            recommended_unit = attr_b.unit
            recommended_source = source_b.source_name
            confidence = conf_b
            reasoning_parts = []

            if source_b.authority_score > source_a.authority_score:
                reasoning_parts.append(
                    f"The {source_b.authority_label.lower()} ({source_b.source_name}) is more authoritative "
                    f"than the {source_a.authority_label.lower()} ({source_a.source_name})"
                )
            if source_b.recency_score > source_a.recency_score:
                reasoning_parts.append("it is more recent")
            if self._evaluate_evidence_quality(attr_b) > self._evaluate_evidence_quality(attr_a):
                reasoning_parts.append("it has stronger evidence")

            reasoning = ". ".join(reasoning_parts) + "." if reasoning_parts else (
                f"{source_b.source_name} has higher overall trust score."
            )
        else:
            recommended_value = attr_a.value
            recommended_unit = attr_a.unit
            recommended_source = source_a.source_name
            confidence = conf_a
            reasoning_parts = []

            if source_a.authority_score > source_b.authority_score:
                reasoning_parts.append(
                    f"The {source_a.authority_label.lower()} ({source_a.source_name}) is more authoritative "
                    f"than the {source_b.authority_label.lower()} ({source_b.source_name})"
                )
            if source_a.recency_score > source_b.recency_score:
                reasoning_parts.append("it is more recent")

            reasoning = ". ".join(reasoning_parts) + "." if reasoning_parts else (
                f"{source_a.source_name} has higher overall trust score."
            )

        return {
            "recommended_value": recommended_value,
            "recommended_unit": recommended_unit,
            "recommended_source": recommended_source,
            "confidence": round(confidence, 4),
            "reasoning": reasoning,
            "trust_a": trust_a,
            "trust_b": trust_b,
            "requires_review": confidence < CONFIDENCE_THRESHOLD,
        }

    def _evaluate_evidence_quality(self, attribute: ExtractedAttribute) -> float:
        """
        Evaluate the quality of evidence supporting an extracted attribute.

        Explicit mention → high score
        Inferred from context → medium score
        No evidence → low score
        """
        if not attribute.evidence:
            return 0.3

        evidence_text = attribute.evidence.text_snippet if attribute.evidence else ""

        if not evidence_text:
            return 0.3

        # Longer, more specific evidence = higher quality
        length_score = min(len(evidence_text) / 100.0, 1.0)

        # Evidence containing the value directly is strongest
        value_present = 0.0
        if attribute.value and attribute.value.lower() in evidence_text.lower():
            value_present = 0.3

        # Page number available = better traceability
        page_bonus = 0.1 if (attribute.evidence and attribute.evidence.page_number) else 0.0

        base_score = 0.4
        score = base_score + (length_score * 0.2) + value_present + page_bonus

        return min(score, 1.0)

    def get_reliability_label(self, confidence: float) -> str:
        """Get human-readable reliability label."""
        if confidence >= 0.90:
            return "Very High"
        elif confidence >= 0.80:
            return "High"
        elif confidence >= 0.70:
            return "Medium-High"
        elif confidence >= 0.55:
            return "Medium"
        elif confidence >= 0.40:
            return "Low"
        else:
            return "Very Low"

    def get_status_label(self, confidence: float, has_conflict: bool = False, reviewed: bool = False) -> str:
        """Get validation status label."""
        if reviewed:
            return "Reviewed"
        if has_conflict:
            return "Requires Review"
        if confidence >= 0.90:
            return "Validated"
        elif confidence >= CONFIDENCE_THRESHOLD:
            return "Provisionally Validated"
        else:
            return "Requires Review"
