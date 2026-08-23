"""Provenza AI - Application Entry Point

Run with: streamlit run run.py
"""

import os
import sys
from pathlib import Path

# Fix sys.path unconditionally for cloud deployment (Streamlit Cloud, Render, HuggingFace)
ROOT_DIR = Path(__file__).resolve().parent
APP_DIR = ROOT_DIR / "app"

for p in [str(ROOT_DIR), str(APP_DIR)]:
    if p not in sys.path:
        sys.path.insert(0, p)

os.chdir(ROOT_DIR)
os.environ["PYTHONPATH"] = f"{ROOT_DIR}{os.pathsep}{APP_DIR}"

from ui.app import main

if __name__ == "__main__":
    main()
