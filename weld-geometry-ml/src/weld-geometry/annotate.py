from pathlib import Path

import cv2


try:
    from config import SCALE_BAR_MM
    from geometry import compute_midpoint, compute_scale
except ImportError:
    from .config import SCALE_BAR_MM
    from .geometry import compute_midpoint, compute_scale


def annotate_image(
    image_path: str | Path,
    zoom: float = 1.2,
) -> dict[str, float]:
    """
    Abre una interfaz gráfica para anotar los 4 puntos clave de la imagen.
    Calcula y muestra automáticamente el punto medio de la base al finalizar.
    Devuelve un diccionario con las coordenadas reales (sin zoom).
    """
    image_path = Path(image_path)
    image = cv2.imread(str(image_path))

    if image is None:
        raise FileNotFoundError(f"No se pudo abrir la imagen: {image_path}")

    # Aplicar zoom
    display_zoomed = cv2.resize(image, None, fx=zoom, fy=zoom, interpolation=cv2.INTER_CUBIC)
    
    window_name = f"Anotando: {image_path.name} (ESC para salir)"
    points: list[tuple[int, int]] = []

    def draw_ui():
        temp = display_zoomed.copy()
        
        # Lógica de instrucciones en pantalla
        if len(points) < 2:
            msg = f"1. Selecciona la ESCALA (2 clicks) | Click {len(points)}/2 [R: reiniciar]"
            color = (0, 255, 0)  # Verde
        elif len(points) < 4:
            msg = f"2. Selecciona la BASE Izq y Der (2 clicks) | Click {len(points) - 2}/2 [R: reiniciar]"
            color = (0, 255, 255)  # Amarillo
        else:
            mx, my = compute_midpoint(
                (float(points[2][0]), float(points[2][1])),
                (float(points[3][0]), float(points[3][1]))
            )
            msg = f"M=({mx:.1f}, {my:.1f}) | [ENTER/ESPACIO] Confirmar | [R] Reintentar | [ESC] Salir"
            color = (255, 255, 255)  # Blanco

        # Barra de estado superior
        banner_width = max(750, int(temp.shape[1]))
        cv2.rectangle(temp, (0, 0), (banner_width, 36), (0, 0, 0), -1)
        cv2.putText(temp, msg, (10, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.55, color, 1)

        # Dibujar puntos marcados
        for pt in points:
            zpt = (round(pt[0] * zoom), round(pt[1] * zoom))
            cv2.drawMarker(temp, zpt, (0, 0, 255), cv2.MARKER_CROSS, 14, 1)
        
        # Línea de escala (verde)
        if len(points) >= 2:
            pt1 = (round(points[0][0] * zoom), round(points[0][1] * zoom))
            pt2 = (round(points[1][0] * zoom), round(points[1][1] * zoom))
            cv2.line(temp, pt1, pt2, (0, 255, 0), 2)
            
        # Línea de base (amarillo)
        if len(points) >= 4:
            pt1 = (round(points[2][0] * zoom), round(points[2][1] * zoom))
            pt2 = (round(points[3][0] * zoom), round(points[3][1] * zoom))
            cv2.line(temp, pt1, pt2, (0, 255, 255), 2)

            # Punto medio M (círculo rojo con borde blanco + etiqueta destacada)
            mx, my = compute_midpoint(
                (float(points[2][0]), float(points[2][1])),
                (float(points[3][0]), float(points[3][1]))
            )
            mid_z = (round(mx * zoom), round(my * zoom))
            cv2.circle(temp, mid_z, 9, (255, 255, 255), -1)  # Borde blanco
            cv2.circle(temp, mid_z, 7, (0, 0, 255), -1)      # Centro rojo
            cv2.putText(
                temp, "M", (mid_z[0] + 12, mid_z[1] + 5),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2
            )

        cv2.imshow(window_name, temp)

    def mouse_callback(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN and len(points) < 4:
            # Guardar coordenadas reales (sin zoom)
            points.append((round(x / zoom), round(y / zoom)))
            draw_ui()

    cv2.namedWindow(window_name, cv2.WINDOW_AUTOSIZE)
    cv2.setMouseCallback(window_name, mouse_callback)
    
    # Dibujo inicial
    draw_ui()

    while True:
        key = cv2.waitKey(20) & 0xFF
        
        if key == 27:  # ESC
            cv2.destroyAllWindows()
            raise RuntimeError("Anotación cancelada por el usuario.")
        
        # 'r' o 'R' reinicia los puntos de la foto actual
        if key in (ord("r"), ord("R")):
            points.clear()
            draw_ui()
            continue

        # Si ya se marcaron los 4 puntos: requiere ENTER (13) o ESPACIO (32) para confirmar
        if len(points) == 4 and key in (13, 32):
            break

    cv2.destroyAllWindows()

    mx, my = compute_midpoint(
        (float(points[2][0]), float(points[2][1])),
        (float(points[3][0]), float(points[3][1]))
    )

    escala = compute_scale(
        (float(points[0][0]), float(points[0][1])),
        (float(points[1][0]), float(points[1][1])),
        SCALE_BAR_MM,
    )

    return {
        "scale_start_x": float(points[0][0]),
        "scale_start_y": float(points[0][1]),
        "scale_end_x": float(points[1][0]),
        "scale_end_y": float(points[1][1]),
        "base_left_x": float(points[2][0]),
        "base_left_y": float(points[2][1]),
        "base_right_x": float(points[3][0]),
        "base_right_y": float(points[3][1]),
        "base_mid_x": round(mx, 2),
        "base_mid_y": round(my, 2),
        "escala_mm_por_px": round(escala, 6),
    }


def save_annotated_image(
    image_path: str | Path,
    coords: dict[str, float],
    output_path: str | Path,
) -> None:
    """Dibuja la escala, la base y el punto medio en la imagen y la guarda en disco."""
    image_path = Path(image_path)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    img = cv2.imread(str(image_path))
    if img is None:
        return

    # Escala (verde)
    s1 = (round(coords["scale_start_x"]), round(coords["scale_start_y"]))
    s2 = (round(coords["scale_end_x"]), round(coords["scale_end_y"]))
    cv2.line(img, s1, s2, (0, 255, 0), 2)
    cv2.drawMarker(img, s1, (0, 255, 0), cv2.MARKER_CROSS, 14, 1)
    cv2.drawMarker(img, s2, (0, 255, 0), cv2.MARKER_CROSS, 14, 1)

    # Base (amarillo)
    bl = (round(coords["base_left_x"]), round(coords["base_left_y"]))
    br = (round(coords["base_right_x"]), round(coords["base_right_y"]))
    cv2.line(img, bl, br, (0, 255, 255), 2)
    cv2.drawMarker(img, bl, (0, 255, 255), cv2.MARKER_CROSS, 14, 1)
    cv2.drawMarker(img, br, (0, 255, 255), cv2.MARKER_CROSS, 14, 1)

    # Punto medio M (círculo rojo con borde blanco y texto)
    mx = round(coords["base_mid_x"])
    my = round(coords["base_mid_y"])
    cv2.circle(img, (mx, my), 7, (255, 255, 255), -1)
    cv2.circle(img, (mx, my), 5, (0, 0, 255), -1)
    cv2.putText(
        img, "M", (mx + 8, my + 4),
        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2
    )

    cv2.imwrite(str(output_path), img)


