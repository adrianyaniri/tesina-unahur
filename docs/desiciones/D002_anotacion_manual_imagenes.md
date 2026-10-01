# D002 — Anotación Manual de las Imágenes

### Contexto y Decisión

En esta etapa inicial, no se implementará detección automática de la barra de escala, la base del cordón ni su contorno. La anotación de puntos clave se realizará de forma **manual** sobre cada imagen para garantizar un dataset de referencia (*ground truth*) controlado, preciso y reproducible.

---

### 1. Escala

En cada imagen se seleccionan manualmente los dos extremos de la barra de escala de referencia (3 mm):

$$ S_1 = (x_1, y_1) $$
$$ S_2 = (x_2, y_2) $$

La distancia en píxeles entre ambos extremos se calcula como:

$$ L_{px} = \sqrt{(x_2 - x_1)^2 + (y_2 - y_1)^2} $$

A partir de esta distancia, se obtiene el factor de escala:

$$ s = \frac{3}{L_{px}} $$

donde $s$ está expresado en **mm/píxel**.

---

### 2. Base del Cordón

Se seleccionan manualmente dos puntos de apoyo de la soldadura sobre la chapa:

$$ B_L = (x_L, y_L) $$
$$ B_R = (x_R, y_R) $$

correspondientes a los extremos izquierdo (*Left*) y derecho (*Right*) de la base del cordón.

> **Nota técnica:** Estos puntos no son todavía puntos de control del modelo de predicción. Son referencias geométricas que se utilizarán posteriormente para construir el sistema de coordenadas local y alinear la geometría.

---

### 3. Justificación del Enfoque Manual

La selección se realiza de manera manual para:
1. **Evitar propagación de errores:** Separar el problema de *anotación geométrica y modelado* del problema de *procesamiento automático de visión por computadora*.
2. **Control de calidad:** Disponer de datos fiables y validados antes de entrenar modelos o ajustar algoritmos automáticos de segmentación.
3. **Reproducibilidad:** Asegurar que las variables de entrada geométricas sean consistentes en los 54 cortes.

---

### 4. Estructura de la Anotación

Cada corte se define mediante **4 puntos manuales (8 coordenadas)**:

```text
        Imagen
           │
     ┌─────┴─────┐
     │           │
   Escala       Base
     │           │
   S1 ─ S2     BL ─ BR
```

Estos 8 valores corresponden a las columnas reservadas en `cortes.csv`:
- `scale_start_x`, `scale_start_y` ($S_1$)
- `scale_end_x`, `scale_end_y` ($S_2$)
- `base_left_x`, `base_left_y` ($B_L$)
- `base_right_x`, `base_right_y` ($B_R$)

---

### 5. Preservación del Dato Original (Píxeles vs. Milímetros)

La anotación persistida en el dataset original se almacenará **estrictamente en píxeles**.

```text
píxeles
   ↓
calibración (s)
   ↓
milímetros
```

> **Principio de diseño:** Almacenar los datos crudos en píxeles preserva la observación original y permite recomputar o corregir la transformación métrica si en el futuro se refina la técnica de calibración, sin degradar el dataset base.
