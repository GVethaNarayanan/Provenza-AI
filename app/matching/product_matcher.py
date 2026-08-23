"""Provenza AI - Product Matcher

Determines whether multiple sources refer to the same product using
multi-tier matching: SKU → fuzzy name → semantic similarity.
"""

import logging
import re
from typing import Optional

from app.models.source import ExtractedAttribute

logger = logging.getLogger(__name__)

# Cache for embedding model
_embedding_model = None


def _get_embedding_model():
    """Lazy-load the sentence-transformers embedding model."""
    global _embedding_model
    if _embedding_model is None:
        try:
            from sentence_transformers import SentenceTransformer
            _embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
            logger.info("Loaded embedding model: all-MiniLM-L6-v2")
        except ImportError:
            logger.warning("sentence-transformers not installed, semantic matching disabled")
        except Exception as e:
            logger.warning(f"Failed to load embedding model: {e}")
    return _embedding_model


def _normalize_for_matching(value: str) -> str:
    """Normalize a string for comparison."""
    if not value:
        return ""
    # Lowercase, remove special chars, collapse whitespace
    cleaned = value.lower().strip()
    cleaned = re.sub(r'[^a-z0-9\s]', ' ', cleaned)
    cleaned = re.sub(r'\s+', ' ', cleaned)
    return cleaned


def _extract_value(attributes: list[ExtractedAttribute], attr_name: str) -> Optional[str]:
    """Extract value for a specific attribute from a list."""
    for attr in attributes:
        if attr.attribute == attr_name and attr.value:
            return attr.value
    return None


def sku_match_score(attrs_a: list[ExtractedAttribute], attrs_b: list[ExtractedAttribute]) -> float:
    """
    Tier 1: Exact SKU/model number matching.
    Returns 1.0 for exact match, 0.0 for no match, partial for substring match.
    """
    sku_a = _extract_value(attrs_a, "model_number")
    sku_b = _extract_value(attrs_b, "model_number")

    if not sku_a or not sku_b:
        return 0.0  # Can't compare

    norm_a = _normalize_for_matching(sku_a)
    norm_b = _normalize_for_matching(sku_b)

    if norm_a == norm_b:
        return 1.0

    # Check if one is a substring of the other (partial model match)
    if norm_a in norm_b or norm_b in norm_a:
        return 0.8

    return 0.0


def fuzzy_name_score(attrs_a: list[ExtractedAttribute], attrs_b: list[ExtractedAttribute]) -> float:
    """
    Tier 2: Fuzzy string matching on product name + brand.
    Uses rapidfuzz for fast fuzzy matching.
    """
    name_a = _extract_value(attrs_a, "product_name") or ""
    name_b = _extract_value(attrs_b, "product_name") or ""
    brand_a = _extract_value(attrs_a, "brand") or ""
    brand_b = _extract_value(attrs_b, "brand") or ""

    # Combine name and brand for matching
    text_a = f"{brand_a} {name_a}".strip()
    text_b = f"{brand_b} {name_b}".strip()

    if not text_a or not text_b:
        return 0.0

    try:
        from rapidfuzz import fuzz
        # Use token_sort_ratio which is order-independent
        score = fuzz.token_sort_ratio(
            _normalize_for_matching(text_a),
            _normalize_for_matching(text_b)
        ) / 100.0
        return score
    except ImportError:
        # Fallback: simple containment check
        norm_a = _normalize_for_matching(text_a)
        norm_b = _normalize_for_matching(text_b)
        if norm_a == norm_b:
            return 1.0
        # Check word overlap
        words_a = set(norm_a.split())
        words_b = set(norm_b.split())
        if not words_a or not words_b:
            return 0.0
        overlap = len(words_a & words_b)
        total = max(len(words_a), len(words_b))
        return overlap / total if total > 0 else 0.0


def semantic_similarity_score(attrs_a: list[ExtractedAttribute], attrs_b: list[ExtractedAttribute]) -> float:
    """
    Tier 3: Semantic similarity using sentence-transformers embeddings.
    Compares overall product descriptions.
    """
    model = _get_embedding_model()
    if model is None:
        return 0.0  # Embeddings not available

    # Build descriptive strings from all attributes
    def build_description(attrs: list[ExtractedAttribute]) -> str:
        parts = []
        for attr in attrs:
            if attr.value:
                if attr.unit:
                    parts.append(f"{attr.display_name or attr.attribute}: {attr.value} {attr.unit}")
                else:
                    parts.append(f"{attr.display_name or attr.attribute}: {attr.value}")
        return ", ".join(parts) if parts else ""

    desc_a = build_description(attrs_a)
    desc_b = build_description(attrs_b)

    if not desc_a or not desc_b:
        return 0.0

    try:
        embeddings = model.encode([desc_a, desc_b])
        # Cosine similarity
        from numpy import dot
        from numpy.linalg import norm
        similarity = float(dot(embeddings[0], embeddings[1]) / (norm(embeddings[0]) * norm(embeddings[1])))
        return max(0.0, similarity)
    except Exception as e:
        logger.warning(f"Semantic similarity failed: {e}")
        return 0.0


def key_attribute_score(attrs_a: list[ExtractedAttribute], attrs_b: list[ExtractedAttribute]) -> float:
    """
    Additional: Compare key attributes (material, size, category) for match.
    """
    key_attrs = ["material", "size", "category", "connection_type"]
    matches = 0
    comparisons = 0

    for attr_name in key_attrs:
        val_a = _extract_value(attrs_a, attr_name)
        val_b = _extract_value(attrs_b, attr_name)

        if val_a and val_b:
            comparisons += 1
            if _normalize_for_matching(val_a) == _normalize_for_matching(val_b):
                matches += 1

    if comparisons == 0:
        return 0.5  # No key attributes to compare

    return matches / comparisons


def calculate_match_confidence(
    attrs_a: list[ExtractedAttribute],
    attrs_b: list[ExtractedAttribute],
    use_embeddings: bool = True,
) -> dict:
    """
    Calculate overall product match confidence across all matching tiers.

    Returns dict with individual scores and overall confidence.
    """
    sku_score = sku_match_score(attrs_a, attrs_b)
    fuzzy_score = fuzzy_name_score(attrs_a, attrs_b)
    key_score = key_attribute_score(attrs_a, attrs_b)

    semantic_score = 0.0
    if use_embeddings:
        semantic_score = semantic_similarity_score(attrs_a, attrs_b)

    # Weighted combination
    # SKU match is most important, then semantic, then fuzzy, then key attrs
    if sku_score >= 0.8:
        # Strong SKU match — high confidence
        weights = {"sku": 0.50, "fuzzy": 0.15, "semantic": 0.20, "key_attr": 0.15}
    elif fuzzy_score >= 0.8:
        # Strong name match
        weights = {"sku": 0.20, "fuzzy": 0.30, "semantic": 0.30, "key_attr": 0.20}
    else:
        # No strong match — balanced
        weights = {"sku": 0.25, "fuzzy": 0.25, "semantic": 0.30, "key_attr": 0.20}

    overall = (
        weights["sku"] * sku_score +
        weights["fuzzy"] * fuzzy_score +
        weights["semantic"] * semantic_score +
        weights["key_attr"] * key_score
    )

    return {
        "overall_confidence": round(min(overall, 1.0), 4),
        "sku_score": round(sku_score, 4),
        "fuzzy_name_score": round(fuzzy_score, 4),
        "semantic_score": round(semantic_score, 4),
        "key_attribute_score": round(key_score, 4),
        "is_match": overall >= 0.70,
        "match_quality": (
            "High" if overall >= 0.90
            else "Medium" if overall >= 0.75
            else "Low" if overall >= 0.60
            else "No Match"
        ),
    }
