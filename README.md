# Predicción de Geometría de Cordones de Soldadura (Weld-Geometry-ML)

Proyecto de investigación y desarrollo para el modelado y predicción de la geometría de cordones de soldadura a partir de parámetros operativos (GMAW / MIG-MAG) utilizando técnicas de visión por computadora y aprendizaje automático.

---

## Documentación para Usuarios

Si sos un usuario nuevo o vas a realizar la anotación de las probetas metalográficas, consultá la guía detallada paso a paso:

👉 **[Guía de Uso del Sistema de Anotación](docs/GUIA_DE_USO.md)**

---

## Comandos Principales

### 1. Entorno y Pruebas Unitarias
El proyecto utiliza [`uv`](https://github.com/astral-sh/uv) como gestor de entorno y dependencias.

```bash
# Ejecutar suite de pruebas automatizadas:
uv run pytest tests/ -v
```

### 2. Anotación de Datos (Ground Truth)
```bash
# Modo de prueba en una sola imagen (Playground):
uv run python main.py

# Anotación continua del dataset completo (guarda en cortes.csv y exporta imágenes):
uv run python src/utils/annotate_dataset.py

# Ajustar factor de aumento según el tamaño de la pantalla:
uv run python src/utils/annotate_dataset.py --zoom 1.0
```

### 3. Visualización y Auditoría
```bash
# Inspección interactiva foto por foto:
uv run python src/utils/visualize_midpoint.py

# Exportación de imágenes anotadas en lote (sin interfaz gráfica):
uv run python src/utils/visualize_midpoint.py --save --no-gui
```

### 4. Regeneración del Dataset desde Cero
```bash
uv run python src/utils/build_dataset.py
```

---

## Estructura del Proyecto

* `src/weld-geometry/`: Módulos principales del sistema.
  * `config.py`: Rutas del proyecto y constantes físicas (`SCALE_BAR_MM = 3.0`).
  * `geometry.py`: Cálculo geométrico puro (puntos medios, factores de escala y validaciones).
  * `annotate.py`: Interfaz de usuario OpenCV para selección de puntos y previsualización.
* `src/utils/`: Scripts utilitarios ejecutables (anotación por lotes, construcción de dataset, visualizadores).
* `data/raw/`: Fotografías originales y planillas de metadatos (`cortes.csv`, `experiencias.csv`).
* `data/processed/visualizaciones/`: Imágenes con las anotaciones y puntos medios superpuestos.
* `tests/`: Batería de pruebas automatizadas para geometría y configuraciones.
* `docs/`: Documentación de arquitectura, decisiones de diseño (`docs/desiciones/`) y guía de usuario.

