"""Provenza AI - LLM Structured Extractor

Uses Gemini API (primary) or OpenAI API (fallback) for structured product
attribute extraction from document text. Includes an intelligent deterministic
heuristic fallback extractor when API keys are missing or offline.
"""

import json
import logging
import re
from typing import Optional

from app.config import (
    GEMINI_API_KEY,
    OPENAI_API_KEY,
    LLM_MODEL_GEMINI,
    LLM_MODEL_OPENAI,
    LLM_TEMPERATURE,
    LLM_MAX_RETRIES,
)
from app.extraction.schemas import EXTRACTION_PROMPT, LLMExtractionResult, LLMExtractedAttribute
from app.models.source import ExtractedAttribute, ExtractedEvidence, ParsedDocument
from app.normalization.attribute_normalizer import normalize_attribute_name, get_display_name

logger = logging.getLogger(__name__)


class LLMExtractor:
    """Extracts structured product attributes using LLMs with a heuristic fallback."""

    def __init__(self):
        self._gemini_model = None
        self._openai_client = None

    def _init_gemini(self):
        """Initialize Gemini API client."""
        if self._gemini_model:
            return True
        if not GEMINI_API_KEY:
            return False
        try:
            import google.generativeai as genai
            genai.configure(api_key=GEMINI_API_KEY)
            self._gemini_model = genai.GenerativeModel(LLM_MODEL_GEMINI)
            return True
        except Exception as e:
            logger.error(f"Gemini init failed: {e}")
            return False

    def _init_openai(self):
        """Initialize OpenAI API client."""
        if self._openai_client:
            return True
        if not OPENAI_API_KEY:
            return False
        try:
            from openai import OpenAI
            self._openai_client = OpenAI(api_key=OPENAI_API_KEY)
            return True
        except Exception as e:
            logger.error(f"OpenAI init failed: {e}")
            return False

    def extract(self, parsed_doc: ParsedDocument) -> list[ExtractedAttribute]:
        """Extract structured attributes from a parsed document."""
        if not parsed_doc.full_text.strip():
            logger.warning(f"Empty document text for source: {parsed_doc.source_name}")
            return []

        # Truncate very long documents to avoid token limits
        doc_text = parsed_doc.full_text[:8000]

        # Try Gemini first, then OpenAI
        result = None
        if self._init_gemini():
            result = self._extract_with_gemini(doc_text)
        if result is None and self._init_openai():
            result = self._extract_with_openai(doc_text)

        if result is not None:
            # Convert LLM result to ExtractedAttribute list
            return self._convert_result(result, parsed_doc)

        logger.info("Using intelligent heuristic/regex fallback extractor...")
        return self._extract_with_heuristic_rules(parsed_doc)

    def _extract_with_gemini(self, doc_text: str) -> Optional[LLMExtractionResult]:
        """Extract using Gemini API."""
        prompt = EXTRACTION_PROMPT.format(document_text=doc_text)

        for attempt in range(LLM_MAX_RETRIES):
            try:
                response = self._gemini_model.generate_content(
                    prompt,
                    generation_config={
                        "temperature": LLM_TEMPERATURE,
                        "response_mime_type": "application/json",
                    },
                )
                raw_text = response.text.strip()
                data = json.loads(raw_text)
                return LLMExtractionResult(**data)

            except json.JSONDecodeError:
                # Try to extract JSON from markdown code blocks
                try:
                    json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', raw_text, re.DOTALL)
                    if json_match:
                        data = json.loads(json_match.group(1))
                        return LLMExtractionResult(**data)
                except Exception:
                    pass
                logger.warning(f"Gemini JSON parse failed, attempt {attempt + 1}")
            except Exception as e:
                logger.warning(f"Gemini extraction failed (attempt {attempt + 1}): {e}")

        return None

    def _extract_with_openai(self, doc_text: str) -> Optional[LLMExtractionResult]:
        """Extract using OpenAI API."""
        prompt = EXTRACTION_PROMPT.format(document_text=doc_text)

        for attempt in range(LLM_MAX_RETRIES):
            try:
                response = self._openai_client.chat.completions.create(
                    model=LLM_MODEL_OPENAI,
                    messages=[
                        {"role": "system", "content": "You are a precise product data extraction specialist. Respond only with valid JSON."},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=LLM_TEMPERATURE,
                    response_format={"type": "json_object"},
                )
                raw_text = response.choices[0].message.content.strip()
                data = json.loads(raw_text)
                return LLMExtractionResult(**data)

            except Exception as e:
                logger.warning(f"OpenAI extraction failed (attempt {attempt + 1}): {e}")

        return None

    def _extract_with_heuristic_rules(self, parsed_doc: ParsedDocument) -> list[ExtractedAttribute]:
        """Fallback deterministic extractor when no LLM API key is available or API is offline."""
        doc_text = parsed_doc.full_text
        attributes = []
        seen_attrs = set()

        # 1. Handle CSV header/value format
        if ',' in doc_text:
            lines = [l.strip() for l in doc_text.split('\n') if l.strip()]
            if len(lines) >= 2 and ',' in lines[0]:
                headers = [h.strip() for h in lines[0].split(',')]
                row = [r.strip() for r in lines[1].split(',')]
                for h, v in zip(headers, row):
                    if h and v:
                        canon_h = normalize_attribute_name(h)
                        disp_h = get_display_name(canon_h)
                        if canon_h not in seen_attrs:
                            seen_attrs.add(canon_h)
                            attributes.append(ExtractedAttribute(
                                attribute=canon_h,
                                display_name=disp_h,
                                value=v,
                                source_id=parsed_doc.source_id,
                                source_name=parsed_doc.source_name,
                                extraction_confidence=0.90,
                                evidence=ExtractedEvidence(
                                    text_snippet=f"{h}: {v}",
                                    source_id=parsed_doc.source_id,
                                    source_name=parsed_doc.source_name,
                                ),
                            ))

        # 2. Key-Value Regex patterns
        patterns = [
            ("product_name", "Product Name", r'(?:Product|Model Name|Item Name|Product Name)[:=]\s*([^\n,]+)'),
            ("model_number", "Model Number", r'(?:Model|SKU|Model Number|Item #)[:=]\s*([^\n,]+)'),
            ("brand", "Brand", r'(?:Brand|Manufacturer|Manufactured by|Maker)[:=]\s*([^\n,]+)'),
            ("category", "Category", r'(?:Category|Type|Product Type)[:=]\s*([^\n,]+)'),
            ("size", "Size", r'(?:Size|Diameter|Dimension)[:=]\s*([^\n,]+)'),
            ("material", "Material", r'(?:Material)[:=]\s*([^\n,]+)'),
            ("body_material", "Body Material", r'(?:Body Material|Housing Material)[:=]\s*([^\n,]+)'),
            ("pressure_rating", "Pressure Rating", r'(?:Pressure Rating|Max Pressure|Pressure)[:=]\s*([^\n,]+)'),
            ("temperature_rating", "Temperature Rating", r'(?:Temperature Rating|Max Temp|Temperature)[:=]\s*([^\n,]+)'),
            ("connection_type", "Connection Type", r'(?:Connection|Connection Type|End Connection)[:=]\s*([^\n,]+)'),
            ("seal_material", "Seal Material", r'(?:Seal|Seal Material|Packing)[:=]\s*([^\n,]+)'),
            ("bore_type", "Bore Type", r'(?:Bore|Bore Type)[:=]\s*([^\n,]+)'),
            ("application", "Application", r'(?:Application|Suitable For)[:=]\s*([^\n,]+)'),
            ("standard", "Standard", r'(?:Standard|Compliance|Design Standard)[:=]\s*([^\n,]+)'),
        ]

        for attr_key, display_name, regex in patterns:
            if attr_key in seen_attrs:
                continue
            match = re.search(regex, doc_text, re.IGNORECASE)
            if match:
                val = match.group(1).strip()
                if val:
                    seen_attrs.add(attr_key)
                    attributes.append(ExtractedAttribute(
                        attribute=attr_key,
                        display_name=display_name,
                        value=val,
                        source_id=parsed_doc.source_id,
                        source_name=parsed_doc.source_name,
                        extraction_confidence=0.88,
                        evidence=ExtractedEvidence(
                            text_snippet=match.group(0),
                            source_id=parsed_doc.source_id,
                            source_name=parsed_doc.source_name,
                        ),
                    ))

        # 3. Colon line-by-line fallback
        for line in doc_text.split('\n'):
            line_str = line.strip()
            if ':' in line_str and not line_str.startswith("TECHNICAL") and not line_str.startswith("http"):
                parts = line_str.split(':', 1)
                k, v = parts[0].strip(), parts[1].strip()
                if k and v and len(k) < 30:
                    canon_k = normalize_attribute_name(k)
                    disp_k = get_display_name(canon_k)
                    if canon_k not in seen_attrs:
                        seen_attrs.add(canon_k)
                        attributes.append(ExtractedAttribute(
                            attribute=canon_k,
                            display_name=disp_k,
                            value=v,
                            source_id=parsed_doc.source_id,
                            source_name=parsed_doc.source_name,
                            extraction_confidence=0.82,
                            evidence=ExtractedEvidence(
                                text_snippet=line_str,
                                source_id=parsed_doc.source_id,
                                source_name=parsed_doc.source_name,
                            ),
                        ))

        return attributes

    def _convert_result(self, result: LLMExtractionResult, parsed_doc: ParsedDocument) -> list[ExtractedAttribute]:
        """Convert LLM extraction result to ExtractedAttribute list."""
        attributes = []

        # Add top-level product info as attributes
        top_level = [
            ("product_name", "Product Name", result.product_name),
            ("model_number", "Model Number", result.model_number),
            ("brand", "Brand", result.brand),
            ("category", "Category", result.category),
        ]

        for attr_name, display_name, value in top_level:
            if value:
                attributes.append(ExtractedAttribute(
                    attribute=attr_name,
                    display_name=display_name,
                    value=value,
                    source_id=parsed_doc.source_id,
                    source_name=parsed_doc.source_name,
                    extraction_confidence=0.90,
                    evidence=ExtractedEvidence(
                        text_snippet=value,
                        source_id=parsed_doc.source_id,
                        source_name=parsed_doc.source_name,
                    ),
                ))

        # Add extracted attributes
        for llm_attr in result.attributes:
            if llm_attr.value is None:
                continue  # Skip null values (not found in source)

            attributes.append(ExtractedAttribute(
                attribute=llm_attr.attribute_name,
                display_name=llm_attr.display_name,
                value=llm_attr.value,
                unit=llm_attr.unit,
                original_value=llm_attr.value,
                original_unit=llm_attr.unit,
                source_id=parsed_doc.source_id,
                source_name=parsed_doc.source_name,
                page_number=llm_attr.page_number,
                extraction_confidence=llm_attr.confidence,
                evidence=ExtractedEvidence(
                    text_snippet=llm_attr.evidence,
                    page_number=llm_attr.page_number,
                    source_id=parsed_doc.source_id,
                    source_name=parsed_doc.source_name,
                ),
            ))

        return attributes
