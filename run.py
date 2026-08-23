"""Provenza AI - Application Entry Point

Run with: streamlit run run.py
"""

import os
import sys
from pathlib import Path

# Unconditionally add project root directory to sys.path for Streamlit Cloud
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
os.environ["PYTHONPATH"] = str(ROOT_DIR)

from ui.app import main

if __name__ == "__main__":
    main()
