"""Provenza AI - Application Configuration"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ============================================================
# Paths
# ============================================================
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DEMO_DIR = DATA_DIR / "demo"
EXPORTS_DIR = BASE_DIR / "exports"
UPLOADS_DIR = BASE_DIR / "uploads"

# Create directories
for d in [DATA_DIR, DEMO_DIR, EXPORTS_DIR, UPLOADS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# ============================================================
# API Keys
# ============================================================
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# ============================================================
# Application Settings
# ============================================================
DEMO_MODE = os.getenv("DEMO_MODE", "true").lower() == "true"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# ============================================================
# Source Authority Levels (configurable)
# ============================================================
SOURCE_AUTHORITY_LEVELS = {
    "manufacturer_spec": {"label": "Current Manufacturer Technical Specification", "score": 0.95},
    "manufacturer_website": {"label": "Manufacturer Website", "score": 0.85},
    "authorized_catalog": {"label": "Authorized Catalog", "score": 0.75},
    "old_catalog": {"label": "Older Catalog", "score": 0.60},
    "third_party": {"label": "Unverified Third-Party Source", "score": 0.40},
}

# ============================================================
# Trust Scoring Weights (configurable, must sum to 1.0)
# ============================================================
TRUST_WEIGHTS = {
    "source_authority": 0.35,
    "recency": 0.25,
    "evidence_quality": 0.20,
    "extraction_confidence": 0.10,
    "cross_source_agreement": 0.10,
}

# ============================================================
# Validation Thresholds
# ============================================================
CONFIDENCE_THRESHOLD = 0.85  # Below this → human review
MATCH_CONFIDENCE_THRESHOLD = 0.70  # Product match threshold
CONFLICT_NUMERICAL_TOLERANCE = 0.01  # % tolerance for numerical comparisons

# ============================================================
# LLM Settings
# ============================================================
LLM_PROVIDER = "gemini"  # "gemini" or "openai"
LLM_MODEL_GEMINI = "gemini-2.0-flash"
LLM_MODEL_OPENAI = "gpt-4o-mini"
LLM_TEMPERATURE = 0.1  # Low temperature for extraction accuracy
LLM_MAX_RETRIES = 3

# ============================================================
# Embedding Settings
# ============================================================
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
