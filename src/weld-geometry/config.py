"""
config.py
---------
Single source of truth for project-wide paths and constants.

Adding a new experiment = zero code changes here.
If the folder structure ever changes, edit only this file.
"""
from __future__ import annotations

from pathlib import Path

# ── Project root (resolves to the repo root regardless of CWD) ───────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# ── Data paths ────────────────────────────────────────────────────────────────
DATA_RAW_DIR         = PROJECT_ROOT / "data" / "raw"
IMAGES_DIR           = DATA_RAW_DIR / "imagenes" / "originales"
CORTES_CSV           = DATA_RAW_DIR / "cortes.csv"
EXPERIENCIAS_CSV     = DATA_RAW_DIR / "experiencias.csv"

DATA_PROCESSED_DIR   = PROJECT_ROOT / "data" / "processed"
VISUALIZATIONS_DIR   = DATA_PROCESSED_DIR / "visualizaciones"

# Mirror copy kept in docs/ for traceability
DOCS_CORTES_CSV      = PROJECT_ROOT / "docs" / "cortes.csv"

# ── UI / display constants ────────────────────────────────────────────────────
# Default zoom factor for annotation tool (1.0 = original size).
# Increase if the image is too small on screen; decrease if too large.
DEFAULT_ANNOTATION_ZOOM: float = 1.2

# Default zoom factor for the visualization viewer (read-only).
DEFAULT_VISUALIZATION_ZOOM: float = 1.0

# ── Scale bar physical length ─────────────────────────────────────────────────
# The white reference bar printed on each cross-section image is 3 mm.
SCALE_BAR_MM: float = 3.0

