"""Provenza AI - Unit Normalizer

Normalizes measurement units to canonical forms while preserving originals.
"""

import re
from typing import Optional


# Unit normalization mappings
UNIT_MAPPINGS = {
    # Length / Size
    "in": "inch",
    "in.": "inch",
    '"': "inch",
    "inches": "inch",
    "inch": "inch",
    "ft": "feet",
    "feet": "feet",
    "foot": "feet",
    "mm": "mm",
    "millimeter": "mm",
    "millimeters": "mm",
    "cm": "cm",
    "centimeter": "cm",
    "centimeters": "cm",
    "m": "m",
    "meter": "m",
    "meters": "m",

    # Pressure
    "psi": "PSI",
    "PSI": "PSI",
    "bar": "bar",
    "bars": "bar",
    "kpa": "kPa",
    "kPa": "kPa",
    "mpa": "MPa",
    "MPa": "MPa",
    "atm": "atm",

    # Temperature
    "°f": "°F",
    "°F": "°F",
    "f": "°F",
    "fahrenheit": "°F",
    "°c": "°C",
    "°C": "°C",
    "c": "°C",
    "celsius": "°C",
    "centigrade": "°C",

    # Weight
    "lb": "lb",
    "lbs": "lb",
    "pounds": "lb",
    "pound": "lb",
    "kg": "kg",
    "kilogram": "kg",
    "kilograms": "kg",
    "g": "g",
    "gram": "g",
    "grams": "g",
    "oz": "oz",
    "ounce": "oz",
    "ounces": "oz",

    # Flow
    "gpm": "GPM",
    "GPM": "GPM",
    "lpm": "LPM",
    "LPM": "LPM",
}

# Patterns for extracting value and unit from combined strings
VALUE_UNIT_PATTERN = re.compile(
    r'^(\d+(?:\.\d+)?)\s*(.+)$'
)

# Patterns for size notations like 2", 1/2", 3/4"
SIZE_PATTERN = re.compile(
    r'^(\d+(?:/\d+)?(?:\.\d+)?)\s*["\u201d]?\s*(?:in\.?|inch(?:es)?)?$',
    re.IGNORECASE
)


def normalize_unit(unit: Optional[str]) -> Optional[str]:
    """Normalize a unit string to its canonical form."""
    if not unit:
        return None

    cleaned = unit.strip().lower()

    # Direct mapping
    for key, canonical in UNIT_MAPPINGS.items():
        if cleaned == key.lower():
            return canonical

    # Return original if no mapping found
    return unit.strip()


def normalize_value_with_unit(value: str, unit: Optional[str] = None) -> tuple[str, Optional[str]]:
    """
    Normalize a value that may contain embedded units.

    Returns (normalized_value, normalized_unit)
    """
    if not value:
        return value, unit

    value = value.strip()

    # If unit is already separate, just normalize both
    if unit:
        return value, normalize_unit(unit)

    # Try to split value and unit
    # Handle patterns like "200 PSI", "2 inch", "150°F"
    match = VALUE_UNIT_PATTERN.match(value)
    if match:
        num_val = match.group(1)
        raw_unit = match.group(2).strip()
        normalized = normalize_unit(raw_unit)
        return num_val, normalized

    # Handle size patterns like '2"', "1/2 in"
    size_match = SIZE_PATTERN.match(value)
    if size_match:
        return size_match.group(1), "inch"

    return value, unit


def normalize_size(value: str) -> tuple[str, str]:
    """Normalize size values specifically."""
    value = value.strip()

    # Remove common size suffixes and normalize
    cleaned = re.sub(r'["\u201d]', '', value)
    cleaned = re.sub(r'\s*(in\.?|inch(?:es)?)\s*$', '', cleaned, flags=re.IGNORECASE)
    cleaned = cleaned.strip()

    if cleaned:
        return cleaned, "inch"
    return value, "inch"


def extract_numeric(value: str) -> Optional[float]:
    """Extract numeric value from a string."""
    if not value:
        return None
    match = re.search(r'(\d+(?:\.\d+)?)', value)
    if match:
        return float(match.group(1))
    return None
