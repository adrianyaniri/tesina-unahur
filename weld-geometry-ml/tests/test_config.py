"""
Tests for config.py

Verifies that project paths, essential assets, and constants are present and valid.
Run with:
    uv run pytest tests/test_config.py -v
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src" / "weld-geometry"))

from config import (
    CORTES_CSV,
    DATA_PROCESSED_DIR,
    DATA_RAW_DIR,
    DEFAULT_ANNOTATION_ZOOM,
    DEFAULT_VISUALIZATION_ZOOM,
    DOCS_CORTES_CSV,
    EXPERIENCIAS_CSV,
    IMAGES_DIR,
    PROJECT_ROOT,
    SCALE_BAR_MM,
    VISUALIZATIONS_DIR,
)


def test_project_root_exists():
    assert PROJECT_ROOT.exists()
    assert (PROJECT_ROOT / "pyproject.toml").exists()


def test_data_paths_exist():
    assert DATA_RAW_DIR.exists()
    assert IMAGES_DIR.exists()
    assert CORTES_CSV.exists()
    assert EXPERIENCIAS_CSV.exists()


def test_processed_directory_structure():
    assert DATA_PROCESSED_DIR.parent.exists()
    # visualizations directory can be created or already exists
    assert VISUALIZATIONS_DIR.name == "visualizaciones"


def test_docs_mirror_exists():
    assert DOCS_CORTES_CSV.parent.exists()


def test_scale_bar_constant():
    assert SCALE_BAR_MM == 3.0


def test_zoom_constants_valid():
    assert DEFAULT_ANNOTATION_ZOOM > 0.0
    assert DEFAULT_VISUALIZATION_ZOOM > 0.0

