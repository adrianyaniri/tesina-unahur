"""
geometry.py
-----------
Pure geometric computations for weld cross-section analysis.
No I/O, no OpenCV dependencies — just math.
"""
from __future__ import annotations


def _validate_point(point: tuple[float, float], name: str) -> None:
    """Raise ValueError if point is not a 2-element numeric tuple."""
    if not (isinstance(point, (tuple, list)) and len(point) == 2):
        raise ValueError(f"{name} must be a 2-element (x, y) tuple, got: {point!r}")
    for i, v in enumerate(point):
        if not isinstance(v, (int, float)):
            raise TypeError(f"{name}[{i}] must be numeric, got {type(v).__name__}: {v!r}")
        if not (v == v):  # NaN check (NaN != NaN)
            raise ValueError(f"{name}[{i}] is NaN — check the CSV for missing data.")


def compute_midpoint(
    base_left: tuple[float, float],
    base_right: tuple[float, float],
) -> tuple[float, float]:
    """
    Return the midpoint M between two base endpoints.

    Parameters
    ----------
    base_left  : (x, y) pixel coordinates of the left base point.
    base_right : (x, y) pixel coordinates of the right base point.

    Returns
    -------
    (mx, my) pixel coordinates of the midpoint, as floats.

    Raises
    ------
    ValueError  : if any coordinate is not a valid 2-element numeric tuple or contains NaN.
    TypeError   : if any coordinate value is not numeric.
    """
    _validate_point(base_left, "base_left")
    _validate_point(base_right, "base_right")

    mx = (base_left[0] + base_right[0]) / 2.0
    my = (base_left[1] + base_right[1]) / 2.0
    return mx, my


def compute_scale(
    scale_start: tuple[float, float],
    scale_end: tuple[float, float],
    longitud_real_mm: float,
) -> float:
    """
    Calcula el factor de escala en mm/píxel a partir de los extremos
    de la barra de referencia y su longitud física conocida.

    Parameters
    ----------
    scale_start     : (x, y) extremo izquierdo de la barra de escala (px).
    scale_end       : (x, y) extremo derecho de la barra de escala (px).
    longitud_real_mm: Longitud física de la barra de escala en milímetros.

    Returns
    -------
    escala_mm_por_px : float — milímetros por píxel.

    Raises
    ------
    ValueError : si los dos puntos son idénticos (distancia cero).
    ValueError : si longitud_real_mm no es positiva.
    """
    _validate_point(scale_start, "scale_start")
    _validate_point(scale_end, "scale_end")

    if not isinstance(longitud_real_mm, (int, float)) or longitud_real_mm <= 0:
        raise ValueError(
            f"longitud_real_mm debe ser un número positivo, recibido: {longitud_real_mm!r}"
        )

    dx = scale_end[0] - scale_start[0]
    dy = scale_end[1] - scale_start[1]
    longitud_px = (dx ** 2 + dy ** 2) ** 0.5

    if longitud_px == 0:
        raise ValueError(
            "Los dos puntos de la barra de escala son idénticos — no se puede calcular la escala."
        )

    return longitud_real_mm / longitud_px

