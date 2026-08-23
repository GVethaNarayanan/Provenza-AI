"""Provenza AI - Material & Terminology Normalizer

Normalizes material names, product terminology, and categorical values.
Preserves original values for traceability.
"""

import re

# Material normalization mappings
MATERIAL_MAPPINGS = {
    # Stainless Steel 304
    "ss304": "304 Stainless Steel",
    "ss 304": "304 Stainless Steel",
    "304 ss": "304 Stainless Steel",
    "304ss": "304 Stainless Steel",
    "304 stainless": "304 Stainless Steel",
    "304 stainless steel": "304 Stainless Steel",
    "stainless steel 304": "304 Stainless Steel",
    "stainless 304": "304 Stainless Steel",
    "aisi 304": "304 Stainless Steel",
    "sus 304": "304 Stainless Steel",
    "ss-304": "304 Stainless Steel",

    # Stainless Steel 316
    "ss316": "316 Stainless Steel",
    "ss 316": "316 Stainless Steel",
    "316 ss": "316 Stainless Steel",
    "316ss": "316 Stainless Steel",
    "316 stainless": "316 Stainless Steel",
    "316 stainless steel": "316 Stainless Steel",
    "stainless steel 316": "316 Stainless Steel",
    "aisi 316": "316 Stainless Steel",
    "ss-316": "316 Stainless Steel",

    # General stainless
    "stainless steel": "Stainless Steel",
    "stainless": "Stainless Steel",
    "ss": "Stainless Steel",

    # Carbon Steel
    "carbon steel": "Carbon Steel",
    "cs": "Carbon Steel",
    "a105": "A105 Carbon Steel",
    "a216 wcb": "A216 WCB Carbon Steel",

    # Brass
    "brass": "Brass",
    "cuzn": "Brass",

    # Bronze
    "bronze": "Bronze",

    # Cast Iron
    "cast iron": "Cast Iron",
    "ci": "Cast Iron",
    "ductile iron": "Ductile Iron",

    # PVC
    "pvc": "PVC",
    "upvc": "UPVC",
    "cpvc": "CPVC",

    # PTFE
    "ptfe": "PTFE",
    "teflon": "PTFE",

    # Rubber seals
    "buna-n": "Buna-N (NBR)",
    "nbr": "Buna-N (NBR)",
    "epdm": "EPDM",
    "viton": "Viton (FKM)",
    "fkm": "Viton (FKM)",
}

# Connection type normalization
CONNECTION_MAPPINGS = {
    "threaded": "Threaded",
    "thread": "Threaded",
    "npt": "NPT Threaded",
    "bsp": "BSP Threaded",
    "bspt": "BSPT Threaded",
    "flanged": "Flanged",
    "flange": "Flanged",
    "welded": "Welded",
    "weld": "Welded",
    "butt weld": "Butt Weld",
    "socket weld": "Socket Weld",
    "sw": "Socket Weld",
    "bw": "Butt Weld",
    "compression": "Compression",
    "tri-clamp": "Tri-Clamp",
    "tri clamp": "Tri-Clamp",
    "triclamp": "Tri-Clamp",
    "push fit": "Push Fit",
    "push-fit": "Push Fit",
    "soldered": "Soldered",
    "solder": "Soldered",
    "grooved": "Grooved",
}

# Bore type normalization
BORE_MAPPINGS = {
    "full bore": "Full Bore",
    "full port": "Full Bore",
    "fb": "Full Bore",
    "reduced bore": "Reduced Bore",
    "reduced port": "Reduced Bore",
    "rb": "Reduced Bore",
    "standard bore": "Standard Bore",
    "standard port": "Standard Bore",
}

# Product category normalization
CATEGORY_MAPPINGS = {
    "ball valve": "Ball Valve",
    "gate valve": "Gate Valve",
    "globe valve": "Globe Valve",
    "check valve": "Check Valve",
    "butterfly valve": "Butterfly Valve",
    "plug valve": "Plug Valve",
    "needle valve": "Needle Valve",
    "diaphragm valve": "Diaphragm Valve",
    "solenoid valve": "Solenoid Valve",
    "relief valve": "Relief Valve",
    "safety valve": "Safety Valve",
    "pressure regulator": "Pressure Regulator",
    "strainer": "Strainer",
    "filter": "Filter",
    "fitting": "Fitting",
    "flange": "Flange",
    "pipe": "Pipe",
    "tube": "Tube",
    "coupling": "Coupling",
    "union": "Union",
    "elbow": "Elbow",
    "tee": "Tee",
    "reducer": "Reducer",
    "actuator": "Actuator",
    "pump": "Pump",
}


def normalize_material(value: str) -> str:
    """Normalize material name to canonical form."""
    if not value:
        return value
    cleaned = value.strip().lower()
    cleaned = re.sub(r'[\-_]+', ' ', cleaned)
    cleaned = re.sub(r'\s+', ' ', cleaned)

    if cleaned in MATERIAL_MAPPINGS:
        return MATERIAL_MAPPINGS[cleaned]

    # Check without spaces
    no_space = cleaned.replace(' ', '')
    for key, canonical in MATERIAL_MAPPINGS.items():
        if no_space == key.replace(' ', ''):
            return canonical

    # Return title-cased original
    return value.strip().title()


def normalize_connection(value: str) -> str:
    """Normalize connection type."""
    if not value:
        return value
    cleaned = value.strip().lower()
    return CONNECTION_MAPPINGS.get(cleaned, value.strip().title())


def normalize_bore(value: str) -> str:
    """Normalize bore type."""
    if not value:
        return value
    cleaned = value.strip().lower()
    return BORE_MAPPINGS.get(cleaned, value.strip().title())


def normalize_category(value: str) -> str:
    """Normalize product category."""
    if not value:
        return value
    cleaned = value.strip().lower()
    return CATEGORY_MAPPINGS.get(cleaned, value.strip().title())


def normalize_value_by_attribute(attribute: str, value: str) -> str:
    """Normalize a value based on its attribute type."""
    normalizers = {
        "material": normalize_material,
        "body_material": normalize_material,
        "seal_material": normalize_material,
        "connection_type": normalize_connection,
        "bore_type": normalize_bore,
        "category": normalize_category,
    }

    normalizer = normalizers.get(attribute)
    if normalizer:
        return normalizer(value)
    return value.strip()
