"""
annotate_dataset.py
-------------------
Orquestador para la anotación progresiva del dataset de cortes de soldadura.
Sigue el principio de responsabilidad única (SRP), separando:
- Carga y persistencia del DataFrame.
- Filtrado de registros pendientes.
- Flujo interactivo de anotación por corte.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

base_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(base_dir / "src" / "weld-geometry"))

from annotate import annotate_image, save_annotated_image
from config import (
    CORTES_CSV,
    DEFAULT_ANNOTATION_ZOOM,
    DOCS_CORTES_CSV,
    IMAGES_DIR,
    SCALE_BAR_MM,
    VISUALIZATIONS_DIR,
)
from geometry import compute_midpoint, compute_scale


def load_dataset() -> pd.DataFrame:
    """Carga el DataFrame de cortes desde la ruta configurada."""
    if not CORTES_CSV.exists():
        raise FileNotFoundError(f"No se encontró el archivo de cortes en {CORTES_CSV}")
    return pd.read_csv(CORTES_CSV)


def save_dataset(df: pd.DataFrame) -> None:
    """Persiste el DataFrame en disco tanto en data/raw como en docs/."""
    df.to_csv(CORTES_CSV, index=False)
    if DOCS_CORTES_CSV.parent.exists():
        df.to_csv(DOCS_CORTES_CSV, index=False)


def backfill_derived_columns(df: pd.DataFrame) -> bool:
    """
    Calcula columnas derivadas (punto medio y escala) para filas ya anotadas
    que no tengan esos valores. Retorna True si se modificó algo.
    """
    changed = False
    for col in ("base_mid_x", "base_mid_y", "escala_mm_por_px"):
        if col not in df.columns:
            df[col] = None
            changed = True

    for idx, row in df.iterrows():
        has_scale = pd.notna(row.get("scale_start_x")) and pd.notna(row.get("scale_end_x"))
        has_base = pd.notna(row.get("base_left_x")) and pd.notna(row.get("base_right_x"))

        if has_base and (pd.isna(row.get("base_mid_x")) or pd.isna(row.get("base_mid_y"))):
            mx, my = compute_midpoint(
                (float(row["base_left_x"]), float(row["base_left_y"])),
                (float(row["base_right_x"]), float(row["base_right_y"])),
            )
            df.at[idx, "base_mid_x"] = round(mx, 2)
            df.at[idx, "base_mid_y"] = round(my, 2)
            changed = True

        if has_scale and pd.isna(row.get("escala_mm_por_px")):
            escala = compute_scale(
                (float(row["scale_start_x"]), float(row["scale_start_y"])),
                (float(row["scale_end_x"]), float(row["scale_end_y"])),
                SCALE_BAR_MM,
            )
            df.at[idx, "escala_mm_por_px"] = round(escala, 6)
            changed = True

    return changed



def get_pending_rows(df: pd.DataFrame, corte_id: int | None = None) -> pd.DataFrame:
    """Filtra y devuelve las filas a anotar (un corte específico o los faltantes)."""
    if corte_id is not None:
        target = df[df["corte_id"] == corte_id]
        if target.empty:
            raise ValueError(f"No se encontró el corte_id={corte_id} en el dataset.")
        return target

    faltantes_mask = (
        df["scale_start_x"].isna()
        | (df["scale_start_x"] == "")
        | (df["scale_start_x"].astype(str) == "nan")
    )
    return df[faltantes_mask]


def sync_annotated_images(df: pd.DataFrame) -> int:
    """
    Genera las imágenes anotadas en disco para todas las filas con datos completos.
    Retorna la cantidad de imágenes generadas.
    """
    VISUALIZATIONS_DIR.mkdir(parents=True, exist_ok=True)
    count = 0
    for _, row in df.iterrows():
        if pd.notna(row.get("scale_start_x")) and pd.notna(row.get("base_mid_x")):
            out_file = VISUALIZATIONS_DIR / f"{Path(row['ruta']).stem}_anotada.jpg"
            if not out_file.exists():
                coords = {
                    k: float(row[k])
                    for k in (
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
                    )
                }
                save_annotated_image(IMAGES_DIR / row["ruta"], coords, out_file)
                count += 1
    return count


def annotate_single_corte(
    df: pd.DataFrame,
    idx: int,
    row: pd.Series,
    zoom: float,
) -> dict[str, float]:
    """Anota una única imagen, actualiza el DataFrame y guarda imagen + CSV."""
    img_path = IMAGES_DIR / row["ruta"]
    coords = annotate_image(img_path, zoom=zoom)

    # Actualizar estado en memoria
    for col, value in coords.items():
        df.at[idx, col] = value

    # Persistencia atómica por corte
    save_dataset(df)

    # Guardar imagen con anotaciones dibujadas
    out_img_path = VISUALIZATIONS_DIR / f"{Path(row['ruta']).stem}_anotada.jpg"
    save_annotated_image(img_path, coords, out_img_path)

    return coords


def parse_cli_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Anotación asistida de cortes de soldadura.")
    parser.add_argument(
        "--zoom",
        type=float,
        default=DEFAULT_ANNOTATION_ZOOM,
        help=f"Factor de escala para visualización (default: {DEFAULT_ANNOTATION_ZOOM}).",
    )
    parser.add_argument(
        "--corte",
        type=int,
        default=None,
        help="Forzar anotación o re-anotación de un corte_id específico.",
    )
    parser.add_argument(
        "--sync",
        action="store_true",
        help="Sincronizar y generar las fotos anotadas en disco para todas las ya guardadas.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_cli_args()

    print(f"Cargando dataset desde: {CORTES_CSV.name}")
    df = load_dataset()

    if backfill_derived_columns(df):
        print("-> Se calcularon y completaron las columnas derivadas (puntos medios y escala) en el CSV.")
        save_dataset(df)

    if args.sync:
        generadas = sync_annotated_images(df)
        print(f"-> Sincronización completada ({generadas} imágenes generadas).")
        return

    try:
        pendientes = get_pending_rows(df, args.corte)
    except ValueError as err:
        print(f"[!] {err}")
        return

    print(f"Imágenes pendientes de anotación: {len(pendientes)} de {len(df)}")
    print(f"Zoom actual: {args.zoom}x")
    print("Controles: [Clicks] Marcar puntos | [R] Reiniciar foto | [ENTER/ESPACIO] Confirmar | [ESC] Salir y guardar\n")

    if len(pendientes) == 0:
        print("¡El dataset ya está completamente anotado!")
        return

    try:
        for idx, row in pendientes.iterrows():
            print(f"Anotando corte {int(row['corte_id'])} ({row['ruta']})... ", end="", flush=True)
            coords = annotate_single_corte(df, idx, row, zoom=args.zoom)
            out_img = f"{Path(row['ruta']).stem}_anotada.jpg"
            print(f"¡Guardado! (M = {coords['base_mid_x']}, {coords['base_mid_y']} | Escala = {coords['escala_mm_por_px']} mm/px) -> {out_img}")

    except RuntimeError as e:
        print(f"\n[!] {e}")
        print("Progreso guardado hasta la última imagen confirmada.")

    print("\nProceso finalizado.")


if __name__ == "__main__":
    main()