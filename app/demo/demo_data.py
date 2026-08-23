"""Provenza AI - Demo Data

Pre-built hero demo scenario: SS-304-V2 Industrial Ball Valve
Complete pipeline data so the demo runs reliably without API keys.

SOURCE A: Old Product Catalog (2023)
SOURCE B: New Technical Specification (2026)

Deliberate conflict: Pressure rating 150 PSI vs 200 PSI
"""

from datetime import datetime

try:
    from app.models.source import (
        SourceMetadata,
        SourceType,
        SourceAuthority,
        ExtractedAttribute,
        ExtractedEvidence,
        ParsedDocument,
        ParsedPage,
    )
    from app.models.reconciliation import (
        ReconciliationResult,
        ReconciliationEntry,
        ConflictDetail,
        AttributeStatus,
    )
    from app.models.product import ProductInput, ValidatedAttribute, ProductRecord
    from app.models.audit import AuditTrail, AuditEntry
except ModuleNotFoundError:
    from models.source import (
        SourceMetadata,
        SourceType,
        SourceAuthority,
        ExtractedAttribute,
        ExtractedEvidence,
        ParsedDocument,
        ParsedPage,
    )
    from models.reconciliation import (
        ReconciliationResult,
        ReconciliationEntry,
        ConflictDetail,
        AttributeStatus,
    )
    from models.product import ProductInput, ValidatedAttribute, ProductRecord
    from models.audit import AuditTrail, AuditEntry


# ============================================================
# Source Metadata
# ============================================================

DEMO_SOURCE_A = SourceMetadata(
    source_id="SRC-A001",
    source_name="Old Product Catalog",
    source_type=SourceType.PDF,
    authority=SourceAuthority.MEDIUM,
    recency_date=datetime(2023, 3, 15),
    description="Legacy product catalog from 2023",
)

DEMO_SOURCE_B = SourceMetadata(
    source_id="SRC-B001",
    source_name="New Technical Specification",
    source_type=SourceType.PDF,
    authority=SourceAuthority.VERY_HIGH,
    recency_date=datetime(2026, 6, 1),
    description="Current manufacturer technical specification sheet",
)


# ============================================================
# Parsed Documents
# ============================================================

DEMO_PARSED_A = ParsedDocument(
    source_id="SRC-A001",
    source_name="Old Product Catalog",
    pages=[ParsedPage(
        page_number=1,
        text_content="""INDUSTRIAL VALVE CATALOG 2023

Product: SS Ball Valve
Size: 2 inch
Material: Stainless Steel
Pressure Rating: 150 PSI
Application: General industrial use
Body Material: Stainless Steel

For more information, contact our sales team.""",
    )],
    full_text="""INDUSTRIAL VALVE CATALOG 2023

Product: SS Ball Valve
Size: 2 inch
Material: Stainless Steel
Pressure Rating: 150 PSI
Application: General industrial use
Body Material: Stainless Steel

For more information, contact our sales team.""",
    total_pages=1,
    parse_method="pdfplumber",
    parse_success=True,
)

DEMO_PARSED_B = ParsedDocument(
    source_id="SRC-B001",
    source_name="New Technical Specification",
    pages=[ParsedPage(
        page_number=1,
        text_content="""TECHNICAL SPECIFICATION SHEET
Date: June 2026

Model: SS-304-V2
Product: Stainless Steel Ball Valve
Size: 2 inch
Connection: Threaded
Material: 304 Stainless Steel
Body Material: 304 Stainless Steel
Seal Material: PTFE
Pressure Rating: 200 PSI
Temperature Rating: 400°F
Bore Type: Full Bore
Standard: API 608, ASME B16.34
Application: Oil & Gas, Chemical Processing, Water Treatment

Manufactured by: ValveTech Industries""",
    )],
    full_text="""TECHNICAL SPECIFICATION SHEET
Date: June 2026

Model: SS-304-V2
Product: Stainless Steel Ball Valve
Size: 2 inch
Connection: Threaded
Material: 304 Stainless Steel
Body Material: 304 Stainless Steel
Seal Material: PTFE
Pressure Rating: 200 PSI
Temperature Rating: 400°F
Bore Type: Full Bore
Standard: API 608, ASME B16.34
Application: Oil & Gas, Chemical Processing, Water Treatment

Manufactured by: ValveTech Industries""",
    total_pages=1,
    parse_method="pdfplumber",
    parse_success=True,
)


# ============================================================
# Extracted Attributes
# ============================================================

def get_demo_attrs_a() -> list[ExtractedAttribute]:
    """Extracted attributes from Source A (Old Catalog)."""
    return [
        ExtractedAttribute(
            attribute="product_name",
            display_name="Product Name",
            value="SS Ball Valve",
            source_id="SRC-A001",
            source_name="Old Product Catalog",
            page_number=1,
            extraction_confidence=0.92,
            evidence=ExtractedEvidence(
                text_snippet="Product: SS Ball Valve",
                page_number=1,
                source_id="SRC-A001",
                source_name="Old Product Catalog",
            ),
        ),
        ExtractedAttribute(
            attribute="size",
            display_name="Size",
            value="2",
            unit="inch",
            original_value="2 inch",
            source_id="SRC-A001",
            source_name="Old Product Catalog",
            page_number=1,
            extraction_confidence=0.95,
            evidence=ExtractedEvidence(
                text_snippet="Size: 2 inch",
                page_number=1,
                source_id="SRC-A001",
                source_name="Old Product Catalog",
            ),
        ),
        ExtractedAttribute(
            attribute="material",
            display_name="Material",
            value="Stainless Steel",
            source_id="SRC-A001",
            source_name="Old Product Catalog",
            page_number=1,
            extraction_confidence=0.90,
            evidence=ExtractedEvidence(
                text_snippet="Material: Stainless Steel",
                page_number=1,
                source_id="SRC-A001",
                source_name="Old Product Catalog",
            ),
        ),
        ExtractedAttribute(
            attribute="pressure_rating",
            display_name="Pressure Rating",
            value="150",
            unit="PSI",
            original_value="150 PSI",
            source_id="SRC-A001",
            source_name="Old Product Catalog",
            page_number=1,
            extraction_confidence=0.93,
            evidence=ExtractedEvidence(
                text_snippet="Pressure Rating: 150 PSI",
                page_number=1,
                source_id="SRC-A001",
                source_name="Old Product Catalog",
            ),
        ),
        ExtractedAttribute(
            attribute="application",
            display_name="Application",
            value="General industrial use",
            source_id="SRC-A001",
            source_name="Old Product Catalog",
            page_number=1,
            extraction_confidence=0.88,
            evidence=ExtractedEvidence(
                text_snippet="Application: General industrial use",
                page_number=1,
                source_id="SRC-A001",
                source_name="Old Product Catalog",
            ),
        ),
        ExtractedAttribute(
            attribute="body_material",
            display_name="Body Material",
            value="Stainless Steel",
            source_id="SRC-A001",
            source_name="Old Product Catalog",
            page_number=1,
            extraction_confidence=0.90,
            evidence=ExtractedEvidence(
                text_snippet="Body Material: Stainless Steel",
                page_number=1,
                source_id="SRC-A001",
                source_name="Old Product Catalog",
            ),
        ),
    ]


def get_demo_attrs_b() -> list[ExtractedAttribute]:
    """Extracted attributes from Source B (New Technical Specification)."""
    return [
        ExtractedAttribute(
            attribute="model_number",
            display_name="Model Number",
            value="SS-304-V2",
            source_id="SRC-B001",
            source_name="New Technical Specification",
            page_number=1,
            extraction_confidence=0.97,
            evidence=ExtractedEvidence(
                text_snippet="Model: SS-304-V2",
                page_number=1,
                source_id="SRC-B001",
                source_name="New Technical Specification",
            ),
        ),
        ExtractedAttribute(
            attribute="product_name",
            display_name="Product Name",
            value="Stainless Steel Ball Valve",
            source_id="SRC-B001",
            source_name="New Technical Specification",
            page_number=1,
            extraction_confidence=0.96,
            evidence=ExtractedEvidence(
                text_snippet="Product: Stainless Steel Ball Valve",
                page_number=1,
                source_id="SRC-B001",
                source_name="New Technical Specification",
            ),
        ),
        ExtractedAttribute(
            attribute="size",
            display_name="Size",
            value="2",
            unit="inch",
            original_value="2 inch",
            source_id="SRC-B001",
            source_name="New Technical Specification",
            page_number=1,
            extraction_confidence=0.97,
            evidence=ExtractedEvidence(
                text_snippet="Size: 2 inch",
                page_number=1,
                source_id="SRC-B001",
                source_name="New Technical Specification",
            ),
        ),
        ExtractedAttribute(
            attribute="connection_type",
            display_name="Connection Type",
            value="Threaded",
            source_id="SRC-B001",
            source_name="New Technical Specification",
            page_number=1,
            extraction_confidence=0.96,
            evidence=ExtractedEvidence(
                text_snippet="Connection: Threaded",
                page_number=1,
                source_id="SRC-B001",
                source_name="New Technical Specification",
            ),
        ),
        ExtractedAttribute(
            attribute="material",
            display_name="Material",
            value="304 Stainless Steel",
            source_id="SRC-B001",
            source_name="New Technical Specification",
            page_number=1,
            extraction_confidence=0.97,
            evidence=ExtractedEvidence(
                text_snippet="Material: 304 Stainless Steel",
                page_number=1,
                source_id="SRC-B001",
                source_name="New Technical Specification",
            ),
        ),
        ExtractedAttribute(
            attribute="body_material",
            display_name="Body Material",
            value="304 Stainless Steel",
            source_id="SRC-B001",
            source_name="New Technical Specification",
            page_number=1,
            extraction_confidence=0.96,
            evidence=ExtractedEvidence(
                text_snippet="Body Material: 304 Stainless Steel",
                page_number=1,
                source_id="SRC-B001",
                source_name="New Technical Specification",
            ),
        ),
        ExtractedAttribute(
            attribute="seal_material",
            display_name="Seal Material",
            value="PTFE",
            source_id="SRC-B001",
            source_name="New Technical Specification",
            page_number=1,
            extraction_confidence=0.96,
            evidence=ExtractedEvidence(
                text_snippet="Seal Material: PTFE",
                page_number=1,
                source_id="SRC-B001",
                source_name="New Technical Specification",
            ),
        ),
        ExtractedAttribute(
            attribute="pressure_rating",
            display_name="Pressure Rating",
            value="200",
            unit="PSI",
            original_value="200 PSI",
            source_id="SRC-B001",
            source_name="New Technical Specification",
            page_number=1,
            extraction_confidence=0.97,
            evidence=ExtractedEvidence(
                text_snippet="Pressure Rating: 200 PSI",
                page_number=1,
                source_id="SRC-B001",
                source_name="New Technical Specification",
            ),
        ),
        ExtractedAttribute(
            attribute="temperature_rating",
            display_name="Temperature Rating",
            value="400",
            unit="°F",
            original_value="400°F",
            source_id="SRC-B001",
            source_name="New Technical Specification",
            page_number=1,
            extraction_confidence=0.95,
            evidence=ExtractedEvidence(
                text_snippet="Temperature Rating: 400°F",
                page_number=1,
                source_id="SRC-B001",
                source_name="New Technical Specification",
            ),
        ),
        ExtractedAttribute(
            attribute="bore_type",
            display_name="Bore Type",
            value="Full Bore",
            source_id="SRC-B001",
            source_name="New Technical Specification",
            page_number=1,
            extraction_confidence=0.96,
            evidence=ExtractedEvidence(
                text_snippet="Bore Type: Full Bore",
                page_number=1,
                source_id="SRC-B001",
                source_name="New Technical Specification",
            ),
        ),
        ExtractedAttribute(
            attribute="standard",
            display_name="Standard",
            value="API 608, ASME B16.34",
            source_id="SRC-B001",
            source_name="New Technical Specification",
            page_number=1,
            extraction_confidence=0.95,
            evidence=ExtractedEvidence(
                text_snippet="Standard: API 608, ASME B16.34",
                page_number=1,
                source_id="SRC-B001",
                source_name="New Technical Specification",
            ),
        ),
        ExtractedAttribute(
            attribute="application",
            display_name="Application",
            value="Oil & Gas, Chemical Processing, Water Treatment",
            source_id="SRC-B001",
            source_name="New Technical Specification",
            page_number=1,
            extraction_confidence=0.94,
            evidence=ExtractedEvidence(
                text_snippet="Application: Oil & Gas, Chemical Processing, Water Treatment",
                page_number=1,
                source_id="SRC-B001",
                source_name="New Technical Specification",
            ),
        ),
        ExtractedAttribute(
            attribute="brand",
            display_name="Brand",
            value="ValveTech Industries",
            source_id="SRC-B001",
            source_name="New Technical Specification",
            page_number=1,
            extraction_confidence=0.93,
            evidence=ExtractedEvidence(
                text_snippet="Manufactured by: ValveTech Industries",
                page_number=1,
                source_id="SRC-B001",
                source_name="New Technical Specification",
            ),
        ),
    ]


# ============================================================
# Product Input
# ============================================================

DEMO_PRODUCT_INPUT = ProductInput(
    product_id="PRD-SS304V2",
    sku="SS-304-V2",
    brand="ValveTech Industries",
    product_name="Stainless Steel Ball Valve",
    category="Ball Valve",
    short_description="2-inch 304 Stainless Steel Ball Valve for industrial applications",
)


# ============================================================
# Product Match Result
# ============================================================

DEMO_MATCH_RESULT = {
    "overall_confidence": 0.96,
    "sku_score": 0.80,
    "fuzzy_name_score": 0.85,
    "semantic_score": 0.92,
    "key_attribute_score": 0.75,
    "is_match": True,
    "match_quality": "High",
}


def run_demo_pipeline():
    """
    Execute the full demo pipeline and return all results.
    Uses the real reconciliation engine with pre-built demo data.
    """
    try:
        from app.reconciliation.engine import ReconciliationEngine
        from app.storage.store import store
    except ModuleNotFoundError:
        from reconciliation.engine import ReconciliationEngine
        from storage.store import store

    engine = ReconciliationEngine()

    # Get demo attributes
    attrs_a = get_demo_attrs_a()
    attrs_b = get_demo_attrs_b()

    # Create audit trail
    audit_trail = store.get_or_create_audit_trail(DEMO_PRODUCT_INPUT.product_id)

    # Run reconciliation (uses real engine — not fake results)
    reconciliation = engine.reconcile(
        attrs_a=attrs_a,
        attrs_b=attrs_b,
        source_a=DEMO_SOURCE_A,
        source_b=DEMO_SOURCE_B,
        product_id=DEMO_PRODUCT_INPUT.product_id,
    )

    # Build product record
    product_record = engine.build_product_record(
        reconciliation=reconciliation,
        product_input={
            "product_id": DEMO_PRODUCT_INPUT.product_id,
            "product_name": DEMO_PRODUCT_INPUT.product_name,
            "brand": DEMO_PRODUCT_INPUT.brand,
            "category": DEMO_PRODUCT_INPUT.category,
            "model_number": DEMO_PRODUCT_INPUT.sku,
        },
        source_a=DEMO_SOURCE_A,
        source_b=DEMO_SOURCE_B,
        audit_trail=audit_trail,
    )

    # Save to store
    store.save_product(product_record)
    store.save_reconciliation(reconciliation)

    return {
        "product_input": DEMO_PRODUCT_INPUT,
        "source_a": DEMO_SOURCE_A,
        "source_b": DEMO_SOURCE_B,
        "attrs_a": attrs_a,
        "attrs_b": attrs_b,
        "match_result": DEMO_MATCH_RESULT,
        "reconciliation": reconciliation,
        "product_record": product_record,
        "audit_trail": audit_trail,
    }
