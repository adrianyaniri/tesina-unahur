# Guía de Uso del Sistema de Medición y Anotación de Soldaduras

Esta guía está diseñada paso a paso para cualquier usuario, **sin necesidad de conocimientos previos de programación**. Explica cómo abrir las imágenes de los cordones de soldadura, marcar los puntos de referencia con el mouse y obtener mediciones físicas exactas de forma automática.

---

## 1. ¿Qué hace este sistema?

En cada ensayo de soldadura se toma una fotografía macrográfica de la sección transversal del cordón. En dicha fotografía existen dos referencias clave:
1. **La barra de escala blanca:** Un patrón físico impreso en la imagen que mide exactamente **3.0 milímetros**.
2. **La línea de base de la chapa:** La unión entre la plancha base y el cordón de soldadura.

Este programa permite marcar con el mouse los extremos de la barra y de la base. A partir de esos clics, el sistema calcula de manera automática e instantánea:
* La equivalencia milímetros por píxel (`escala_mm_por_px`).
* El punto medio geométrico de la base (**origen de coordenadas $M$**).
* Guarda los datos en una planilla de cálculo (`cortes.csv`).
* Genera una copia de la imagen con las líneas y el punto medio dibujados para control de calidad visual.

---

## 2. Preparación inicial

### Paso 1: Abrir la terminal
En Windows, abre la aplicación **PowerShell** o la terminal integrada de tu editor (por ejemplo, VS Code con `Ctrl + ñ`).

### Paso 2: Verificar la ubicación
Asegúrate de estar ubicado en la carpeta del proyecto:
```powershell
c:\Dev\Unahur\Tesina\weld-geometry-ml
```
*(Si no estás en esa carpeta, no ejecutes comandos hasta situarte en ella).*

---

## 3. Modo de Prueba (Anotar una sola imagen de práctica)

Antes de trabajar sobre el dataset completo, puedes probar la herramienta en una imagen de muestra sin alterar ningún archivo de datos.

### Ejecución:
Escribe el siguiente comando y presiona **Enter**:
```bash
uv run python main.py
```

### ¿Cómo interactuar con la ventana?

Se abrirá una ventana titulada `Anotando: Cordon1_Seccion 1 horizontal C1.jpg`:

```
+-------------------------------------------------------------------------------+
| [1. Selecciona la ESCALA (2 clicks)]                                          |
+-------------------------------------------------------------------------------+
|                                                                               |
|      (Clic 1) -------- [Barra de escala 3 mm] -------- (Clic 2)               |
|                                                                               |
|                                  /\                                           |
|                                 /  \  <- Cordón de soldadura                  |
|      (Clic 3) _________________/____\_________________ (Clic 4)               |
|      Base Izq                                          Base Der               |
+-------------------------------------------------------------------------------+
```

Debes realizar **4 clics con el botón izquierdo del mouse** en el siguiente orden:

1. **Clic 1:** Extremo izquierdo de la barra de escala blanca.
2. **Clic 2:** Extremo derecho de la barra de escala blanca.
   *(Aparecerá una línea verde que une ambos extremos).*
3. **Clic 3:** Extremo izquierdo de la base del cordón sobre la chapa.
4. **Clic 4:** Extremo derecho de la base del cordón sobre la chapa.
   *(Aparecerá una línea amarilla en la base).*

### ¿Qué ocurre tras el 4to clic?
Automáticamente aparece un **círculo rojo con la letra M** en el punto medio de la base y la barra superior cambiará a:
```
M=(X, Y) | [ENTER/ESPACIO] Confirmar | [R] Reintentar | [ESC] Salir
```

### Controles del teclado en la ventana:
* **Barra Espaciadora o Enter:** Confirma la anotación y cierra la ventana mostrando los resultados por consola.
* **Tecla R:** Si te equivocaste en algún clic, presiona `R` en cualquier momento para reiniciar la imagen en blanco y volver a marcar.
* **Tecla ESC:** Cancela la operación y cierra la ventana sin guardar nada.

---

## 4. Modo de Trabajo Real (Anotación del Dataset Completo)

Este es el comando principal para procesar todas las fotografías del proyecto de forma continua y ordenada.

### Ejecución:
```bash
uv run python src/utils/annotate_dataset.py
```

### Comportamiento del programa:
1. **Reanudación automática:** El programa busca cuáles imágenes están pendientes y abre directamente la primera que falte anotar. Si ya habías anotado imágenes previamente, **no las vuelve a pedir**.
2. **Guardado inmediato:** Al presionar **Enter** tras los 4 clics:
   * Los datos numéricos se guardan al instante en `data/raw/cortes.csv` (y su réplica en `docs/cortes.csv`).
   * La foto con las líneas verde, amarilla y el punto rojo se guarda automáticamente en `data/processed/visualizaciones/`.
   * El sistema abre de forma inmediata la siguiente fotografía pendiente.
3. **Interrupción segura:** Puedes anotar la cantidad de fotos que desees. Cuando quieras descansar o interrumpir el trabajo, presiona la tecla **ESC**. Todo lo confirmado hasta ese momento queda guardado en disco de manera segura. Al volver a ejecutar el comando otro día, continuará exactamente en la siguiente foto.

### Ajuste del tamaño de visualización (Zoom):
Si tu pantalla es pequeña (por ejemplo, en una notebook) o la imagen se ve demasiado grande:
```bash
# Tamaño 100% original (sin aumento):
uv run python src/utils/annotate_dataset.py --zoom 1.0

# Tamaño recomendado por defecto (aumento del 20%):
uv run python src/utils/annotate_dataset.py --zoom 1.2
```

### Rehacer o inspeccionar un corte específico:
Si deseas volver a marcar un corte puntual (por ejemplo, el corte número 5):
```bash
uv run python src/utils/annotate_dataset.py --corte 5
```

---

## 5. Dónde encontrar y cómo revisar los resultados

Una vez anotadas las imágenes, los resultados quedan disponibles en dos formatos:

### 1. Planilla de datos numéricos
El archivo principal es:
📁 `data/raw/cortes.csv`

Puedes abrirlo con Excel o cualquier editor de texto. Contiene las siguientes columnas:
* `corte_id`, `experimento_id`, `seccion`, `ruta`: Identificadores del corte y nombre del archivo de imagen.
* `scale_start_x`, `scale_start_y`, `scale_end_x`, `scale_end_y`: Coordenadas en píxeles de los extremos de la barra de escala.
* `base_left_x`, `base_left_y`, `base_right_x`, `base_right_y`: Coordenadas en píxeles de los extremos de la base del cordón.
* `base_mid_x`, `base_mid_y`: Coordenadas calculadas del punto medio de la base.
* `escala_mm_por_px`: Factor de escala calculado ($3.0\text{ mm} / \text{longitud en píxeles}$). Por ejemplo, `0.024590` mm/px.
* Parámetros de soldadura asociados: Voltaje, Corriente, Velocidad de alambre y Flujo de gas.

### 2. Archivos de imagen anotados
Las imágenes resultantes se guardan en:
📁 `data/processed/visualizaciones/`

Cada archivo lleva el nombre original con el sufijo `_anotada.jpg`. Puedes abrirlas con el visor de fotos de Windows para auditar visualmente que la línea de base y el punto medio estén correctamente posicionados.

---

## 6. Visor y Auditoría de Anotaciones

Para revisar rápidamente en pantalla las imágenes que ya fueron anotadas:

```bash
# Avanzar foto por foto en pantalla (presiona cualquier tecla para la siguiente, ESC para salir):
uv run python src/utils/visualize_midpoint.py

# Si deseas regenerar o exportar todas las imágenes a disco sin interactuar con ventanas:
uv run python src/utils/visualize_midpoint.py --save --no-gui
```

---

## 7. ¿Cómo reiniciar todo desde cero? (Paso de emergencia)

Si por alguna razón necesitas borrar todas las anotaciones y comenzar el dataset completamente limpio:

```bash
uv run python src/utils/build_dataset.py
```
> **Advertencia:** Este comando restablece `cortes.csv`, dejando todas las columnas geométricas vacías y listo para empezar una nueva sesión de anotación desde la foto 1.

---

## 8. Preguntas Frecuentes y Solución de Problemas

### 1. Hice clic en un lugar equivocado, ¿qué hago?
No te preocupes. Simplemente presiona la letra **R** en tu teclado. Los puntos marcados en esa foto se borrarán y podrás volver a hacer los 4 clics desde el inicio.

### 2. La ventana no responde al teclado
Asegúrate de hacer un clic sobre la ventana de la imagen para que tenga el foco del sistema operativo antes de presionar las teclas.

### 3. La imagen se sale de la pantalla
Ejecuta el script indicando un factor de zoom menor:
```bash
uv run python src/utils/annotate_dataset.py --zoom 1.0
```

### 4. ¿Cómo sé cuántas imágenes me faltan anotar?
Al iniciar el script `annotate_dataset.py`, la primera línea de la terminal te informará el estado:
```text
Imágenes pendientes de anotación: 39 de 54
```

