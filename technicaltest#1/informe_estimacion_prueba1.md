
# **Informe de Estimación de Costos de Equipos para Proyecto de Construcción**

## **1. Explicación del caso**

Una empresa del sector constructor se encuentra en etapa de planeación para un proyecto con una duración estimada de 36 meses. Para garantizar una correcta asignación presupuestal, requiere establecer un **precio base confiable** para dos equipos esenciales, cuyos costos dependen directamente del comportamiento de tres materias primas: **X**, **Y** y **Z**.

El objetivo central es construir un proceso reproducible que:

* Integre las fuentes históricas de precios.
* Limpie y normalice los datos independientemente del formato recibido.
* Calcule los precios base de ambos equipos.
* Documente resultados y proporcione insumos para análisis futuro (forecasting, simulación).

Las fórmulas de composición de costos son:

* **Equipo 1:**
  `Precio = 0.2 * X + 0.8 * Y`

* **Equipo 2:**
  `Precio = (X + Y + Z) / 3`

Este informe describe el enfoque técnico adoptado, los supuestos utilizados, la estrategia de resolución, los resultados obtenidos y las oportunidades de mejora.

---

## **2. Supuestos**

1. **Fuentes de datos:**
   Los archivos `X.csv`, `Y.csv` y `Z.csv` representan precios unitarios por periodo de cada materia prima.

2. **Naturaleza de los datos:**
   Los archivos pueden venir con:

   * Diferentes delimitadores (`;`, `,`, `|`, tab).
   * Formatos numéricos europeos (coma decimal).
   * Fechas en múltiples formatos.
   * Variaciones de encabezados con o sin BOM.

   El proceso debe manejar estos casos dinámicamente.

3. **Composición del precio:**
   Se asume que los porcentajes indicados por el caso representan la participación exacta dentro del costo base de los equipos, sin costos agregados ni sobrecargos adicionales.

4. **Temporalidad:**
   Si los insumos no presentan fechas, se asume una indexación secuencial válida para análisis descriptivo.

5. **Simulación y forecasting:**
   Para proyecciones a 36 meses:

   * Se utiliza Prophet para estimar tendencias futuras.
   * Se emplea Monte Carlo con volatilidad histórica como proxy de incertidumbre.

---

## **3. Formas para resolver el caso y opción seleccionada**

### **Alternativas metodológicas posibles**

1. **Cálculo determinista**

   * Limpieza y normalización de datos.
   * Aplicación directa de las fórmulas de composición.
   * Generación de salidas agregadas y gráficas.

2. **Modelos de series temporales (Forecasting)**

   * ARIMA, ETS o Prophet.
   * Proyección de la tendencia de cada materia prima o del precio final del equipo.

3. **Simulación estocástica (Monte Carlo)**

   * Modela incertidumbre futura en base a retornos históricos.
   * Proporciona intervalos de confianza (p5, p50, p95).

4. **Enfoque híbrido**
   Forecast para tendencia + Monte Carlo para volatilidad residual.

---

### **Opción adoptada en esta prueba**

Se implementó un **pipeline completo y funcional** que incluye:

* Limpieza robusta de archivos.
* Normalización de formatos numéricos.
* Conversión flexible de fechas.
* Generación del cálculo base de los equipos.
* Producción de salidas consolidadas.
* Gráfica comparativa de los equipos.
* Forecasting a 36 meses con Prophet.
* Simulación Monte Carlo con 10.000 escenarios.
* Tests unitarios.

Este enfoque maximiza reproducibilidad, calidad de código y claridad técnica, y aborda tanto la estimación base como escenarios futuros.

---

## **4. Resultados del análisis de los datos y los modelos**

### **4.1 Resultados del proceso de estimación**

El script `estimation_script.py` genera los siguientes artefactos:

* `estimated_equipment_prices.csv`:
  dataset final con valores calculados de `equip1` y `equip2`.

* `summary_estimates.csv`:
  resumen estadístico de X, Y, Z y de los precios resultantes de ambos equipos.

* `equipment_prices_plot.png`:
  visualización temporal que compara los dos equipos.

**Ejemplo de estructura en el archivo procesado:**

| X | Y | Z | equip1 | equip2 |
| - | - | - | ------ | ------ |
| … | … | … | …      | …      |

*(La tabla exacta se genera automáticamente al ejecutar el pipeline.)*

---

### **4.2 Forecasting a 36 meses**

El archivo:

* `forecast_equip1.csv`
* `forecast_equip2.csv`

Incluye columnas:

* `ds` (fecha futura)
* `yhat` (predicción)
* `yhat_lower`, `yhat_upper` (banda de confianza)

Interpretación general:

* El Equipo 1 muestra mayor sensibilidad a Y, por lo que reproduce sus oscilaciones.
* El Equipo 2 tiende a moverse de forma más estable al ser un promedio simple de tres materias primas.

---

### **4.3 Simulación Monte Carlo**

Los archivos:

* `montecarlo_equip1.csv`
* `montecarlo_equip2.csv`

Incluyen percentiles por mes:

| month | p5 | p50 | p95 |
| ----- | -- | --- | --- |

Interpretación general:

* p5 → escenario conservador.
* p50 → caso base.
* p95 → escenario adverso (volatilidad alta).

Esto permite costear mejor riesgos en contratos y adquisiciones.

---

## **5. Futuros ajustes o mejoras**

1. **Ampliar el modelo con costos adicionales:**
   Mano de obra, transporte, mantenimiento, gasto operativo, CAPEX/OPEX.

2. **Incorporar escenarios financieros:**

   * Tasas de inflación.
   * Índices de commodities.
   * Variaciones dólar/mercado global.

3. **Estrategias de compra complementarias:**

   * Hedging financiero.
   * Acuerdos de precio fijo por ventana de tiempo.
   * Análisis de proveedores alternativos.

4. **Modelos más avanzados:**

   * Prophet + regresores externos.
   * LSTM para series altamente no lineales.
   * Monte Carlo correlacionado para X, Y, Z.

5. **Orquestación en cloud:**

   * Implementarlo como job en AWS/Azure para obtener puntos extra y garantizar escalabilidad.

---

## **6. Apreciaciones y comentarios (opcional)**

El caso representa un escenario frecuente en planificación de proyectos de construcción, donde la volatilidad de materias primas puede afectar de manera significativa el presupuesto final. Un enfoque basado en datos —como el implementado aquí— permite reducir incertidumbre, soportar decisiones de compra y proyectar escenarios con mayor precisión.

La automatización del pipeline asegura reproducibilidad, claridad técnica y la posibilidad de integrarse a procesos más amplios de budgeting corporativo.

---

## **Archivos entregados**

### **Código**

* `src/estimation_script.py`
* `src/forecasting_36m.py`
* `src/montecarlo_36m.py`

### **Datos**

* `data/raw/` (X.csv, Y.csv, Z.csv)
* `data/cleaned/` (archivos normalizados)
* `data/processed/` (resultados)

### **Resultados**

* `estimated_equipment_prices.csv`
* `summary_estimates.csv`
* `forecast/forecast_equipX.csv`
* `montecarlo/montecarlo_equipX.csv`
* `equipment_prices_plot.png`

### **Testing**

* `tests/test_estimation.py`
* `pytest.ini`

### **Documentación**

* `informe_estimacion.md` (este archivo)
* `README.md`

---

Si deseas, puedo generar también:

* **README profesional**
* **Presentación ejecutiva (markdown o PowerPoint)**
* **Versión del informe más corta o más técnica**, según lo que quieras entregar.

¿Quieres que lo prepare?
