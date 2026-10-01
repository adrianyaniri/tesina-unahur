from pathlib import Path
import cv2
from matplotlib.pyplot import imshow


def select_scale_point(
        imagen_path: str  | Path,
) -> tuple[tuple[int, int], tuple[int, int]]:
    image = cv2.imread(imagen_path)

    if image is None:
        raise FileNotFoundError(f"No se pudo abrir imagen {imagen_path}")

    window_name = " Seleccionar barra de escala"
    points: list[tuple[int, int]] = []

    def mouse_callback(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            return
        if len(points) >= 2:
            return
        points.append((x, y))

        cv2.circle(image, (x, y), 1, (0, 0, 255), -1)
        cv2,imshow(window_name, image)
        cv2.setMouseCallback(window_name, mouse_callback)

        while len(points) < 2:
            cv2.imshow(window_name, image)

            key = cv2.waitKey(20) & 0xFF

            if key == 27:
                cv2.destroyAllWindows()
                raise RuntimeError("Selección cancelada por el usuario")

        cv2.destroyAllWindows()

        return points[0], points[1]