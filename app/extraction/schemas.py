"""Provenza AI - Extraction Schemas

Pydantic schemas for structured LLM output validation.
These schemas ensure the LLM returns well-formed, traceable data.
"""

from typing import Optional
from pydantic import BaseModel, Field


class LLMExtractedAttribute(BaseModel):
    """Schema for a single attribute extracted by the LLM."""
    attribute_name: str = Field(description="Canonical attribute name (e.g., 'material', 'pressure_rating')")
    display_name: str = Field(description="Human-readable attribute name (e.g., 'Material', 'Pressure Rating')")
    value: Optional[str] = Field(None, description="Extracted value. null if not found in source.")
    unit: Optional[str] = Field(None, description="Unit of measurement if applicable")
    evidence: str = Field("", description="Exact text snippet from source that supports this extraction")
    page_number: Optional[int] = Field(None, description="Page number where evidence was found")
    confidence: float = Field(0.0, description="Confidence score 0.0-1.0")


class LLMExtractionResult(BaseModel):
    """Schema for the complete extraction result from an LLM."""
    product_name: str = Field("", description="Extracted product name")
    model_number: str = Field("", description="Model/SKU number")
    brand: str = Field("", description="Brand/manufacturer name")
    category: str = Field("", description="Product category")
    attributes: list[LLMExtractedAttribute] = Field(
        default_factory=list,
        description="List of extracted product attributes"
    )


# The extraction prompt template
EXTRACTION_PROMPT = """You are a precise industrial product data extraction specialist.

TASK: Extract structured product attributes from the following source document text.

CRITICAL RULES:
1. ONLY extract information that is EXPLICITLY stated in the source text.
2. Do NOT infer, guess, or hallucinate any attribute values.
3. If an attribute is not mentioned, set its value to null.
4. For each extracted value, provide the exact text evidence from the source.
5. Set confidence based on how explicit and clear the information is:
   - 0.95-1.0: Explicitly and clearly stated
   - 0.80-0.94: Stated but may need interpretation
   - 0.60-0.79: Partially stated or inferred from context
   - Below 0.60: Uncertain, do not extract

ATTRIBUTES TO EXTRACT:
- product_name: Full product name
- model_number: Model or SKU number
- brand: Brand or manufacturer
- category: Product category (e.g., "Ball Valve", "Gate Valve")
- material: Material composition
- size: Product size/dimensions
- pressure_rating: Pressure rating with units
- temperature_rating: Temperature rating with units
- connection_type: Connection type (e.g., Threaded, Flanged, Welded)
- body_material: Body material if different from general material
- seal_material: Seal/gasket material
- end_connection: End connection type
- bore_type: Bore type (Full bore, Reduced bore)
- standard: Applicable standards (e.g., API, ANSI, ASME)
- weight: Product weight
- color: Product color if specified
- application: Intended application/use

SOURCE DOCUMENT TEXT:
---
{document_text}
---

Respond with a JSON object matching this exact schema:
{{
  "product_name": "string",
  "model_number": "string",
  "brand": "string",
  "category": "string",
  "attributes": [
    {{
      "attribute_name": "string (e.g., 'material')",
      "display_name": "string (e.g., 'Material')",
      "value": "string or null",
      "unit": "string or null",
      "evidence": "exact text snippet from source",
      "page_number": int_or_null,
      "confidence": float_0_to_1
    }}
  ]
}}
"""
