"""Provenza AI - Reconciliation Engine

Core innovation: Multi-source product attribute reconciliation.
Compares, classifies, and resolves attributes across sources.
"""

import logging
from typing import Optional

from app.models.source import ExtractedAttribute, SourceMetadata
from app.models.reconciliation import (
    AttributeStatus,
    ReconciliationEntry,
    ReconciliationResult,
    ConflictDetail,
)
from app.models.product import ValidatedAttribute, ProductRecord
from app.models.audit import AuditTrail
from app.reconciliation.conflict_detector import ConflictDetector
from app.reconciliation.trust_scorer import TrustScorer
from app.normalization.attribute_normalizer import normalize_attribute_name, get_display_name
from app.normalization.unit_normalizer import normalize_value_with_unit
from app.normalization.material_normalizer import normalize_value_by_attribute

logger = logging.getLogger(__name__)


class ReconciliationEngine:
    """
    Core reconciliation engine that compares attributes across sources
    and classifies them as MATCH, ENRICHED, CONFLICT, MISSING, or UNCERTAIN.
    """

    def __init__(self):
        self.trust_scorer = TrustScorer()
        self.conflict_detector = ConflictDetector(self.trust_scorer)

    def normalize_attributes(
        self,
        attributes: list[ExtractedAttribute],
    ) -> list[ExtractedAttribute]:
        """Normalize all attribute names, values, and units."""
        normalized = []
        for attr in attributes:
            # Preserve originals
            attr.original_value = attr.original_value or attr.value
            attr.original_unit = attr.original_unit or attr.unit

            # Normalize attribute name
            canonical_name = normalize_attribute_name(attr.attribute)
            attr.attribute = canonical_name
            attr.display_name = get_display_name(canonical_name)

            # Normalize value based on attribute type
            if attr.value:
                attr.value = normalize_value_by_attribute(canonical_name, attr.value)

            # Normalize units
            NUMERICAL_ATTRS = {"pressure_rating", "temperature_rating", "size", "weight", "flow_rate", "cv_value"}
            if attr.value and attr.unit:
                attr.value, attr.unit = normalize_value_with_unit(attr.value, attr.unit)
            elif attr.value and not attr.unit and canonical_name in NUMERICAL_ATTRS:
                # Only try to extract embedded unit for numerical attributes
                attr.value, attr.unit = normalize_value_with_unit(attr.value)

            normalized.append(attr)

        return normalized

    def reconcile(
        self,
        attrs_a: list[ExtractedAttribute],
        attrs_b: list[ExtractedAttribute],
        source_a: SourceMetadata,
        source_b: SourceMetadata,
        product_id: str = "",
    ) -> ReconciliationResult:
        """
        Reconcile attributes from two sources.

        Classifies each attribute as MATCH, ENRICHED, CONFLICT, MISSING, or UNCERTAIN.
        """
        # Normalize first
        attrs_a = self.normalize_attributes(attrs_a)
        attrs_b = self.normalize_attributes(attrs_b)

        # Build lookup dicts by canonical attribute name
        dict_a = {}
        for attr in attrs_a:
            if attr.attribute not in dict_a:  # Keep first occurrence
                dict_a[attr.attribute] = attr

        dict_b = {}
        for attr in attrs_b:
            if attr.attribute not in dict_b:
                dict_b[attr.attribute] = attr

        # Get all unique attributes
        all_attributes = set(dict_a.keys()) | set(dict_b.keys())

        entries = []
        conflicts = []
        enriched_attrs = []

        for attr_name in sorted(all_attributes):
            a = dict_a.get(attr_name)
            b = dict_b.get(attr_name)

            entry = self._reconcile_attribute(
                attr_name, a, b, source_a, source_b
            )
            entries.append(entry)

            if entry.status == AttributeStatus.CONFLICT and entry.conflict:
                conflicts.append(entry.conflict)
            elif entry.status == AttributeStatus.ENRICHED:
                enriched_attrs.append(attr_name)

        result = ReconciliationResult(
            product_id=product_id,
            entries=entries,
            conflicts=conflicts,
            enriched_attributes=enriched_attrs,
            total_attributes=len(entries),
            matched_count=sum(1 for e in entries if e.status == AttributeStatus.MATCH),
            enriched_count=sum(1 for e in entries if e.status == AttributeStatus.ENRICHED),
            conflict_count=sum(1 for e in entries if e.status == AttributeStatus.CONFLICT),
            missing_count=sum(1 for e in entries if e.status == AttributeStatus.MISSING),
        )

        return result

    def _reconcile_attribute(
        self,
        attr_name: str,
        attr_a: Optional[ExtractedAttribute],
        attr_b: Optional[ExtractedAttribute],
        source_a: SourceMetadata,
        source_b: SourceMetadata,
    ) -> ReconciliationEntry:
        """Reconcile a single attribute across two sources."""

        display_name = get_display_name(attr_name)

        # Case 1: Both sources have the attribute
        if attr_a and attr_b and attr_a.value and attr_b.value:
            # Check for conflict
            conflict = self.conflict_detector.detect_conflict(
                attr_name, attr_a, attr_b, source_a, source_b
            )

            if conflict:
                # CONFLICT
                return ReconciliationEntry(
                    attribute=attr_name,
                    display_name=display_name,
                    status=AttributeStatus.CONFLICT,
                    source_a_value=attr_a.value,
                    source_a_unit=attr_a.unit,
                    source_a_name=source_a.source_name,
                    source_b_value=attr_b.value,
                    source_b_unit=attr_b.unit,
                    source_b_name=source_b.source_name,
                    final_value=conflict.recommendation,
                    final_unit=conflict.recommendation_unit,
                    final_source=conflict.recommendation_source,
                    confidence=conflict.confidence,
                    conflict=conflict,
                )
            else:
                # MATCH - use highest-confidence source
                trust_a = self.trust_scorer.calculate_field_confidence(
                    attr_a, source_a, cross_source_agreement=1.0
                )
                trust_b = self.trust_scorer.calculate_field_confidence(
                    attr_b, source_b, cross_source_agreement=1.0
                )

                # Use the more detailed/specific value if both match
                if len(str(attr_b.value or "")) > len(str(attr_a.value or "")):
                    winner = attr_b
                    winner_source = source_b
                    confidence = max(trust_a["final_confidence"], trust_b["final_confidence"])
                else:
                    winner = attr_a
                    winner_source = source_a
                    confidence = max(trust_a["final_confidence"], trust_b["final_confidence"])

                # Cross-source agreement boosts confidence
                confidence = min(confidence * 1.05, 1.0)

                return ReconciliationEntry(
                    attribute=attr_name,
                    display_name=display_name,
                    status=AttributeStatus.MATCH,
                    source_a_value=attr_a.value,
                    source_a_unit=attr_a.unit,
                    source_a_name=source_a.source_name,
                    source_b_value=attr_b.value,
                    source_b_unit=attr_b.unit,
                    source_b_name=source_b.source_name,
                    final_value=winner.value,
                    final_unit=winner.unit,
                    final_source="Both Sources",
                    confidence=round(confidence, 4),
                )

        # Case 2: Only Source A has the attribute
        elif attr_a and attr_a.value and (not attr_b or not attr_b.value):
            trust_a = self.trust_scorer.calculate_field_confidence(
                attr_a, source_a, cross_source_agreement=0.5
            )
            return ReconciliationEntry(
                attribute=attr_name,
                display_name=display_name,
                status=AttributeStatus.ENRICHED if not attr_b else AttributeStatus.MATCH,
                source_a_value=attr_a.value,
                source_a_unit=attr_a.unit,
                source_a_name=source_a.source_name,
                source_b_value=None,
                source_b_name=source_b.source_name,
                final_value=attr_a.value,
                final_unit=attr_a.unit,
                final_source=source_a.source_name,
                confidence=trust_a["final_confidence"],
            )

        # Case 3: Only Source B has the attribute
        elif attr_b and attr_b.value and (not attr_a or not attr_a.value):
            trust_b = self.trust_scorer.calculate_field_confidence(
                attr_b, source_b, cross_source_agreement=0.5
            )
            return ReconciliationEntry(
                attribute=attr_name,
                display_name=display_name,
                status=AttributeStatus.ENRICHED,
                source_a_value=None,
                source_a_name=source_a.source_name,
                source_b_value=attr_b.value,
                source_b_unit=attr_b.unit,
                source_b_name=source_b.source_name,
                final_value=attr_b.value,
                final_unit=attr_b.unit,
                final_source=source_b.source_name,
                confidence=trust_b["final_confidence"],
            )

        # Case 4: Neither source has the attribute
        else:
            return ReconciliationEntry(
                attribute=attr_name,
                display_name=display_name,
                status=AttributeStatus.MISSING,
                source_a_name=source_a.source_name,
                source_b_name=source_b.source_name,
                confidence=0.0,
            )

    def build_product_record(
        self,
        reconciliation: ReconciliationResult,
        product_input: dict,
        source_a: SourceMetadata,
        source_b: SourceMetadata,
        audit_trail: Optional[AuditTrail] = None,
    ) -> ProductRecord:
        """Build final commerce-ready product record from reconciliation result."""

        attributes = {}
        for entry in reconciliation.entries:
            if entry.final_value is None and entry.status == AttributeStatus.MISSING:
                continue

            has_conflict = entry.status == AttributeStatus.CONFLICT
            reviewed = (
                entry.conflict and
                entry.conflict.reviewer_decision is not None
            ) if has_conflict else False

            status = self.trust_scorer.get_status_label(
                entry.confidence,
                has_conflict=has_conflict,
                reviewed=reviewed,
            )

            # Determine evidence text
            evidence = ""
            if entry.conflict:
                evidence = entry.conflict.source_b_evidence or entry.conflict.source_a_evidence
            elif entry.source_b_value:
                evidence = f"{entry.display_name}: {entry.source_b_value}"
                if entry.source_b_unit:
                    evidence += f" {entry.source_b_unit}"
            elif entry.source_a_value:
                evidence = f"{entry.display_name}: {entry.source_a_value}"
                if entry.source_a_unit:
                    evidence += f" {entry.source_a_unit}"

            # Determine reasoning
            reasoning = ""
            if entry.conflict:
                reasoning = entry.conflict.reasoning
            elif entry.status == AttributeStatus.MATCH:
                reasoning = "Value confirmed across both sources."
            elif entry.status == AttributeStatus.ENRICHED:
                reasoning = f"Attribute enriched from {entry.final_source}."

            # Use reviewer overrides if present
            final_value = entry.final_value
            final_unit = entry.final_unit
            reviewer_decision = None
            if entry.conflict and entry.conflict.reviewer_decision:
                reviewer_decision = entry.conflict.reviewer_decision
                if entry.conflict.reviewer_value:
                    final_value = entry.conflict.reviewer_value
                status = "Reviewed"

            validated = ValidatedAttribute(
                attribute=entry.attribute,
                display_name=entry.display_name,
                value=final_value,
                unit=final_unit,
                source=entry.final_source,
                source_id="",
                evidence=evidence,
                confidence=entry.confidence,
                status=status.lower().replace(' ', '_'),
                reasoning=reasoning,
                review_required=has_conflict and not reviewed,
                reviewer_decision=reviewer_decision,
            )

            attributes[entry.attribute] = validated

            # Add audit entry
            if audit_trail:
                audit_trail.add_entry(
                    attribute=entry.attribute,
                    display_name=entry.display_name,
                    new_value=f"{final_value} {final_unit}" if final_unit else final_value,
                    source=entry.final_source,
                    confidence=entry.confidence,
                    action=entry.status.value,
                    decision="auto_validated" if not has_conflict else "requires_review",
                    reviewer="system",
                    product_name=product_input.get("product_name", ""),
                )

        record = ProductRecord(
            product_id=product_input.get("product_id", ""),
            product_name=product_input.get("product_name", ""),
            brand=product_input.get("brand", ""),
            category=product_input.get("category", ""),
            model_number=product_input.get("model_number", ""),
            attributes=attributes,
            conflicts=[c.model_dump() for c in reconciliation.conflicts],
            enriched_attributes=reconciliation.enriched_attributes,
            sources=[
                {
                    "source_id": source_a.source_id,
                    "name": source_a.source_name,
                    "type": source_a.source_type.value,
                    "authority": source_a.authority.value,
                    "authority_label": source_a.authority_label,
                },
                {
                    "source_id": source_b.source_id,
                    "name": source_b.source_name,
                    "type": source_b.source_type.value,
                    "authority": source_b.authority.value,
                    "authority_label": source_b.authority_label,
                },
            ],
        )

        record.calculate_overall_confidence()
        record.get_review_status()

        return record
