"""
visualize_midpoint.py
---------------------
Reads cortes.csv (annotated rows only) and displays each image with:
  - Scale bar endpoints   (green line + crosses)
  - Base left / right     (yellow line + crosses)
  - Midpoint M            (red filled circle)

Usage:
    uv run python src/utils/visualize_midpoint.py
    uv run python src/utils/visualize_midpoint.py --corte 1
    uv run python src/utils/visualize_midpoint.py --save
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import cv2
import pandas as pd

base_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(base_dir / "src" / "weld-geometry"))

from config import (  # noqa: E402
    CORTES_CSV,
    DEFAULT_VISUALIZATION_ZOOM,
    IMAGES_DIR,
    VISUALIZATIONS_DIR,
)
from geometry import compute_midpoint  # noqa: E402

# ── visual constants ──────────────────────────────────────────────────────────
COLOR_SCALE  = (0, 255, 0)    # green
COLOR_BASE   = (0, 255, 255)  # yellow
COLOR_MID    = (0, 0, 255)    # red
MARKER_SIZE  = 18
MARKER_THICK = 1
MID_RADIUS   = 8


def _z(coord: float, zoom: float) -> int:
    """Scale a pixel coordinate by zoom factor."""
    return round(coord * zoom)


def draw_annotations(image, row: pd.Series, zoom: float = ZOOM):
    """
    Draw scale bar, base line, and midpoint on a (possibly zoomed) copy of image.
    Returns the annotated image.
    """
    img = cv2.resize(image, None, fx=zoom, fy=zoom, interpolation=cv2.INTER_CUBIC)

    s1 = (_z(row.scale_start_x, zoom), _z(row.scale_start_y, zoom))
    s2 = (_z(row.scale_end_x,   zoom), _z(row.scale_end_y,   zoom))
    bl = (_z(row.base_left_x,   zoom), _z(row.base_left_y,   zoom))
    br = (_z(row.base_right_x,  zoom), _z(row.base_right_y,  zoom))

    mx, my = compute_midpoint(
        (row.base_left_x, row.base_left_y),
        (row.base_right_x, row.base_right_y),
    )
    mid = (_z(mx, zoom), _z(my, zoom))

    # Scale bar
    cv2.line(img, s1, s2, COLOR_SCALE, 2)
    for pt in (s1, s2):
        cv2.drawMarker(img, pt, COLOR_SCALE, cv2.MARKER_CROSS, MARKER_SIZE, MARKER_THICK)

    # Base line
    cv2.line(img, bl, br, COLOR_BASE, 2)
    for pt in (bl, br):
        cv2.drawMarker(img, pt, COLOR_BASE, cv2.MARKER_CROSS, MARKER_SIZE, MARKER_THICK)

    # Midpoint
    cv2.circle(img, mid, MID_RADIUS, COLOR_MID, -1)
    cv2.putText(
        img, "M",
        (mid[0] + 10, mid[1] - 6),
        cv2.FONT_HERSHEY_SIMPLEX, 0.55, COLOR_MID, 2,
    )

    return img, (mx, my)


def run(filter_corte: int | None, save: bool, zoom: float = DEFAULT_VISUALIZATION_ZOOM, no_gui: bool = False) -> None:
    df = pd.read_csv(CORTES_CSV)

    # Keep only annotated rows
    annotated = df[df["scale_start_x"].notna()].copy()

    if filter_corte is not None:
        annotated = annotated[annotated["corte_id"] == filter_corte]

    if annotated.empty:
        print("No hay imágenes anotadas para mostrar.")
        return

    if save:
        VISUALIZATIONS_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Visualizando {len(annotated)} corte(s) (Zoom {zoom}x). Presioná cualquier tecla para avanzar, ESC para salir.")

    for _, row in annotated.iterrows():
        img_path = IMAGES_DIR / row["ruta"]
        image = cv2.imread(str(img_path))
        if image is None:
            print(f"  [!] No se pudo abrir: {img_path.name}")
            continue

        annotated_img, (mx, my) = draw_annotations(image, row, zoom=zoom)

        # Info banner at top
        label = f"Corte {int(row.corte_id)} | M = ({mx:.1f}, {my:.1f}) px"
        cv2.rectangle(annotated_img, (0, 0), (520, 38), (0, 0, 0), -1)
        cv2.putText(annotated_img, label, (10, 26),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)

        print(f"  Corte {int(row.corte_id):2d} — {row['ruta']}")
        print(f"    BL=({row.base_left_x:.0f}, {row.base_left_y:.0f})  "
              f"BR=({row.base_right_x:.0f}, {row.base_right_y:.0f})  "
              f"M=({mx:.1f}, {my:.1f})")

        if save:
            stem = Path(row["ruta"]).stem
            out_path = VISUALIZATIONS_DIR / f"{stem}_midpoint.jpg"
            cv2.imwrite(str(out_path), annotated_img)
            print(f"    Guardado en: {out_path.relative_to(VISUALIZATIONS_DIR.parent.parent)}")

        if not no_gui:
            window = f"Corte {int(row.corte_id)} — {Path(row['ruta']).name}"
            cv2.namedWindow(window, cv2.WINDOW_AUTOSIZE)
            cv2.imshow(window, annotated_img)

            key = cv2.waitKey(0) & 0xFF
            cv2.destroyAllWindows()

            if key == 27:  # ESC
                print("Salida anticipada.")
                break

    print("Listo.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Visualize base midpoint on weld images.")
    parser.add_argument("--corte", type=int, default=None,
                        help="Show only a specific corte_id.")
    parser.add_argument("--save", action="store_true",
                        help="Save annotated images to data/processed/visualizaciones/.")
    parser.add_argument("--zoom", type=float, default=DEFAULT_VISUALIZATION_ZOOM,
                        help=f"Factor de escala para la imagen (default: {DEFAULT_VISUALIZATION_ZOOM}).")
    parser.add_argument("--no-gui", action="store_true",
                        help="Guardar sin abrir ventanas interactivas.")
    args = parser.parse_args()
    run(args.corte, args.save, zoom=args.zoom, no_gui=args.no_gui)


if __name__ == "__main__":
    main()

