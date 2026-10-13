# D003 — Sistema de Coordenadas Local

### Decisión

Cada corte transversal utilizará un **sistema de coordenadas cartesiano local**, con origen en el punto medio de los extremos de la base del cordón ($M$), eje $+X$ hacia la derecha y eje $+Y$ hacia arriba.

Las coordenadas geométricas del contorno y del modelo se expresarán finalmente en **milímetros (mm)**.

---

### Contexto y Puntos de Referencia

Para cada corte disponemos de las coordenadas de la base anotadas manualmente (en píxeles):

$$ B_L = (x_L, y_L) \quad \text{(extremo izquierdo)} $$
$$ B_R = (x_R, y_R) \quad \text{(extremo derecho)} $$

---

### 1. Definición del Origen ($M$)

El origen del sistema local se define como el punto medio entre ambos extremos de la base:

$$ M = \left( \frac{x_L + x_R}{2}, \; \frac{y_L + y_R}{2} \right) $$

En el sistema de coordenadas intrínseco del cordón:

$$ M = (0, 0) $$

---

### 2. Orientación de los Ejes

Se establece un sistema cartesiano estándar:
- **$+X$**: Hacia la derecha (ancho del cordón).
- **$+Y$**: Hacia arriba (altura/refuerzo del cordón sobre la chapa).

```text
                 +Y
                  ↑
                  │
                  │
                  │
                  M──────────────→ +X
                (0,0)
```

**Interpretación física directa:**
- $x > 0$: Lado derecho respecto del centro.
- $x < 0$: Lado izquierdo respecto del centro.
- $y > 0$: Por encima de la base (sobreespesor o refuerzo del cordón).
- $y < 0$: Por debajo de la base (penetración en el material base).

---

### 3. Invarianza respecto de la Imagen

Al fijar un sistema de coordenadas relativo a $M$:
- No afecta el desplazamiento del cordón dentro del encuadre de la foto.
- No afecta el tamaño o resolución de la imagen.
- No afecta la ubicación de la barra de escala.
- No requiere que el fotógrafo o metalógrafo haya centrado perfectamente la muestra.

La geometría queda descrita de forma **intrínseca y desacoplada de la cámara**.

---

### 4. Transformación de Coordenadas: Píxeles $\to$ Milímetros

#### Paso 1: Centrado en píxeles respecto de $M$
$$ \Delta x_{px} = x_{px} - M_x $$
$$ \Delta y_{px} = y_{px} - M_y $$

#### Paso 2: Conversión métrica con inversión de eje vertical
En visión por computadora y matrices de imagen, el eje $Y$ crece hacia abajo (origen en la esquina superior izquierda). Para que $+Y$ apunte físicamente hacia arriba en el sistema cartesiano, se invierte el signo:

$$ x_{mm} = (x_{px} - M_x) \cdot s $$
$$ y_{mm} = -(y_{px} - M_y) \cdot s $$

donde:

$$ s = \frac{3}{L_{px}} \quad [\text{mm/píxel}] $$

es el factor de escala individual de cada corte (definido en D002).

---

### Resumen de la Decisión

> **D003:** Cada corte utilizará un sistema de coordenadas cartesiano local, con origen en el punto medio de los extremos de la base del cordón, eje $X$ positivo hacia la derecha y eje $Y$ positivo hacia arriba. Las coordenadas geométricas se expresarán en milímetros.
