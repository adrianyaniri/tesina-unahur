# D001 — Estructura del dataset

### Desición

Separar los datos en dos fuentes:

- **\*experiencia.csv:** Información de las 18 experiencias de la soldadura
- **\*cortes.csv:** Infomación de los 54 cortes/imagenes asociados a esas experiencias.

> La relación se establece mediante **_experiencia_id_**

### Justificación

Una experiencia de soldadura define un conjunto de parámetros de proceso y tiene tres cortes asociados. Los parámetros son, por lo tanto, propiedades de la **experiencia** , mientras que las coordenadas de la escala, los puntos de la base y la ruta de la imagen son propiedades del **corte** .

Esto evita almacenar repetidamente los parámetros de una misma experiencia en cada uno de sus tres cortes.

### Estructura

> experiments.csv
> 1 experiencia
> │
> ├── corte
> ├── corte
> └── corte

**_experciencias.csv_**

> experiencia_id
> perilla_voltaje
> perilla_vel_alambre
> flujo_gas
> voltaje
> corriente

**_cortes.csv_**

> corte_id
> experiencia_id
> ruta
> scale_start_x
> scale_start_y
> scale_end_x
> scale_end_y
> base_left_x
> base_left_y
> base_right_x
> base_right_y

### Decisión adicional

Los datos derivados como:

- escala en mm/píxel;
- sistema de coordenadas local;
- puntos de control;
- coordenadas finales en mm;

  **no forman parte de los datos originales** . Serán generados posteriormente mediante procesos documentados.

Esto es importante porque nos permite modificar un algoritmo de procesamiento sin alterar los datos originales.
