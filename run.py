"""Provenza AI - Application Entry Point

Run with: streamlit run run.py
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from ui.app import main

if __name__ == "__main__":
    main()
