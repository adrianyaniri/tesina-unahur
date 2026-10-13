from pathlib import Path

import cv2


def select_scale_points(
    image_path: str | Path,
    zoom: float = 2.0,
) -> tuple[tuple[int, int], tuple[int, int]]:
    """Open an image and let the user click on the two endpoints of the scale bar.

    Returns:
        A tuple (S1, S2) where each element is an (x, y) pixel coordinate.

    Raises:
        FileNotFoundError: If the image cannot be opened.
        RuntimeError: If the user cancels the selection with Escape.
    """
    image_path = Path(image_path)
    image = cv2.imread(str(image_path))

    if image is None:
        raise FileNotFoundError(f"Cannot open image: {image_path}")

    # Aumentamos el tamaño de la imagen por software
    display_zoomed = cv2.resize(image, None, fx=zoom, fy=zoom, interpolation=cv2.INTER_CUBIC)
    
    window_name = "Seleciona los puntos de la barra de escala  [click x2 — ESC to cancel]"
    points: list[tuple[int, int]] = []

    def mouse_callback(event, x, y, flags, param) -> None:
        if event != cv2.EVENT_LBUTTONDOWN:
            return
        if len(points) >= 2:
            return

        # Coordenada real (deshaciendo el zoom)
        real_x = round(x / zoom)
        real_y = round(y / zoom)
        points.append((real_x, real_y))

        # Dibujamos una cruz en la imagen aumentada
        cv2.drawMarker(display_zoomed, (x, y), (0, 0, 255), markerType=cv2.MARKER_CROSS, markerSize=15, thickness=1)

        if len(points) == 2:
            pt1_zoomed = (round(points[0][0] * zoom), round(points[0][1] * zoom))
            cv2.line(display_zoomed, pt1_zoomed, (x, y), (0, 255, 0), 1)

        cv2.imshow(window_name, display_zoomed)

    cv2.namedWindow(window_name, cv2.WINDOW_AUTOSIZE)
    cv2.imshow(window_name, display_zoomed)
    cv2.setMouseCallback(window_name, mouse_callback)

    while len(points) < 2:
        key = cv2.waitKey(20) & 0xFF
        if key == 27:  # ESC
            cv2.destroyAllWindows()
            raise RuntimeError("Selection cancelled by user.")

    cv2.waitKey(500)
    cv2.destroyAllWindows()

    return points[0], points[1]


def compute_scale(
    s1: tuple[int, int],
    s2: tuple[int, int],
    reference_mm: float = 3.0,
) -> float:
    """Compute scale factor in mm/pixel from two annotated endpoints.

    Args:
        s1: First endpoint (x1, y1) in pixels.
        s2: Second endpoint (x2, y2) in pixels.
        reference_mm: Known physical length of the scale bar in millimetres.

    Returns:
        Scale factor s = reference_mm / L_px  (mm/pixel).
    """
    x1, y1 = s1
    x2, y2 = s2
    l_px = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5

    if l_px == 0:
        raise ValueError("The two points are identical — cannot compute scale.")

    return reference_mm / l_px