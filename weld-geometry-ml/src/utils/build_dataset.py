"""
build_dataset.py
----------------
Genera el archivo cortes.csv combinando los metadatos de las experiencias
y las imágenes de los cortes metalográficos existentes.
Usa config.py para rutas centralizadas.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import pandas as pd

base_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(base_dir / "src" / "weld-geometry"))

from config import (
    CORTES_CSV,
    DOCS_CORTES_CSV,
    EXPERIENCIAS_CSV,
    IMAGES_DIR,
)

# Patrón para identificar imágenes válidas: ej. Cordon1_Seccion 1 horizontal C1.jpg
IMG_PATTERN = re.compile(
    r"Cordon(\d+)_Seccion\s*(\d+)\s*horizontal\s*C\1\.jpg", re.IGNORECASE
)

# Columnas de anotación geométrica iniciales
GEOMETRY_COLUMNS = [
    "scale_start_x",
    "scale_start_y",
    "scale_end_x",
    "scale_end_y",
    "base_left_x",
    "base_left_y",
    "base_right_x",
    "base_right_y",
    "base_mid_x",
    "base_mid_y",
    "escala_mm_por_px",
]


def find_image_records() -> list[dict]:
    """Escanea IMAGES_DIR y parsea experimento_id y sección de cada corte."""
    if not IMAGES_DIR.exists():
        raise FileNotFoundError(f"No existe el directorio de imágenes: {IMAGES_DIR}")

    records = []
    for file_path in IMAGES_DIR.iterdir():
        if file_path.suffix.lower() == ".jpg":
            match = IMG_PATTERN.match(file_path.name)
            if match:
                cordon = int(match.group(1))
                seccion = int(match.group(2))
                # La experiencia 15 queda excluida por definición del proyecto
                if cordon != 15:
                    records.append({
                        "ruta": file_path.name,
                        "experimento_id": cordon,
                        "seccion": seccion,
                    })
    return records


def generate_cortes() -> pd.DataFrame:
    """Construye y persiste el dataset cortes.csv unificando imágenes y experiencias."""
    if not EXPERIENCIAS_CSV.exists():
        raise FileNotFoundError(f"No se encontró el archivo de experiencias en {EXPERIENCIAS_CSV}")

    df_exp = pd.read_csv(EXPERIENCIAS_CSV)
    records = find_image_records()
    df_imgs = pd.DataFrame(records)

    if df_imgs.empty:
        raise ValueError(f"No se encontraron imágenes válidas en {IMAGES_DIR}")

    merged = pd.merge(
        df_imgs,
        df_exp,
        left_on="experimento_id",
        right_on="experiencia_id",
        how="inner",
    )
    merged = merged.sort_values(by=["experimento_id", "seccion"]).reset_index(drop=True)
    merged["corte_id"] = range(1, len(merged) + 1)

    for col in GEOMETRY_COLUMNS:
        merged[col] = ""

    # Orden explícito de columnas
    metadata_cols = [
        col for col in df_exp.columns if col not in ("experiencia_id", "experimento_id")
    ]
    final_cols = (
        ["corte_id", "experimento_id", "seccion", "ruta"]
        + GEOMETRY_COLUMNS
        + metadata_cols
    )
    df_final = merged[final_cols]

    # Guardar en raw y en docs (para trazabilidad en repositorio)
    df_final.to_csv(CORTES_CSV, index=False, encoding="utf-8")
    if DOCS_CORTES_CSV.parent.exists():
        df_final.to_csv(DOCS_CORTES_CSV, index=False, encoding="utf-8")

    print(f"Dataset generado exitosamente con {len(df_final)} cortes en {CORTES_CSV.name}.")
    return df_final


if __name__ == "__main__":
    generate_cortes()
