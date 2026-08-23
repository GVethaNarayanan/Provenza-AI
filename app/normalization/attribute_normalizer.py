"""Provenza AI - Attribute Name Normalizer

Normalizes attribute names and values to canonical forms.
"""

import re

# Canonical attribute name mappings
ATTRIBUTE_NAME_MAPPINGS = {
    # Product identity
    "product_name": "product_name",
    "product name": "product_name",
    "name": "product_name",
    "product": "product_name",
    "description": "product_name",

    "model_number": "model_number",
    "model number": "model_number",
    "model": "model_number",
    "model no": "model_number",
    "model no.": "model_number",
    "part number": "model_number",
    "part no": "model_number",
    "sku": "model_number",

    "brand": "brand",
    "manufacturer": "brand",
    "mfg": "brand",
    "mfr": "brand",
    "make": "brand",

    "category": "category",
    "type": "category",
    "product type": "category",
    "product category": "category",

    # Physical attributes
    "material": "material",
    "materials": "material",
    "body material": "body_material",
    "body_material": "body_material",
    "construction": "material",

    "size": "size",
    "nominal size": "size",
    "pipe size": "size",
    "port size": "size",
    "dimensions": "size",
    "dimension": "size",

    "weight": "weight",
    "net weight": "weight",
    "gross weight": "weight",

    "color": "color",
    "colour": "color",
    "finish": "color",

    # Performance
    "pressure_rating": "pressure_rating",
    "pressure rating": "pressure_rating",
    "pressure": "pressure_rating",
    "max pressure": "pressure_rating",
    "maximum pressure": "pressure_rating",
    "working pressure": "pressure_rating",
    "rated pressure": "pressure_rating",
    "max working pressure": "pressure_rating",

    "temperature_rating": "temperature_rating",
    "temperature rating": "temperature_rating",
    "temperature": "temperature_rating",
    "max temperature": "temperature_rating",
    "operating temperature": "temperature_rating",
    "temperature range": "temperature_rating",

    # Connection
    "connection_type": "connection_type",
    "connection type": "connection_type",
    "connection": "connection_type",
    "end connection": "connection_type",
    "end_connection": "connection_type",
    "end type": "connection_type",

    # Valve-specific
    "bore_type": "bore_type",
    "bore type": "bore_type",
    "bore": "bore_type",
    "port type": "bore_type",

    "seal_material": "seal_material",
    "seal material": "seal_material",
    "seal": "seal_material",
    "gasket material": "seal_material",
    "packing": "seal_material",

    "standard": "standard",
    "standards": "standard",
    "certification": "standard",
    "certifications": "standard",
    "compliance": "standard",

    "application": "application",
    "applications": "application",
    "use": "application",
    "suitable for": "application",
}

# Display name mappings
DISPLAY_NAMES = {
    "product_name": "Product Name",
    "model_number": "Model Number",
    "brand": "Brand",
    "category": "Category",
    "material": "Material",
    "body_material": "Body Material",
    "size": "Size",
    "weight": "Weight",
    "color": "Color",
    "pressure_rating": "Pressure Rating",
    "temperature_rating": "Temperature Rating",
    "connection_type": "Connection Type",
    "bore_type": "Bore Type",
    "seal_material": "Seal Material",
    "standard": "Standard",
    "application": "Application",
}


def normalize_attribute_name(name: str) -> str:
    """Normalize an attribute name to its canonical form."""
    if not name:
        return name

    cleaned = name.strip().lower()
    cleaned = re.sub(r'[_\-]+', ' ', cleaned)
    cleaned = re.sub(r'\s+', ' ', cleaned)

    # Check direct mapping
    if cleaned in ATTRIBUTE_NAME_MAPPINGS:
        return ATTRIBUTE_NAME_MAPPINGS[cleaned]

    # Check with underscores restored
    underscored = cleaned.replace(' ', '_')
    if underscored in ATTRIBUTE_NAME_MAPPINGS:
        return ATTRIBUTE_NAME_MAPPINGS[underscored]

    # Return as-is with underscores
    return underscored


def get_display_name(canonical_name: str) -> str:
    """Get the human-readable display name for a canonical attribute name."""
    if canonical_name in DISPLAY_NAMES:
        return DISPLAY_NAMES[canonical_name]
    # Fallback: convert underscores to spaces and title case
    return canonical_name.replace('_', ' ').title()
