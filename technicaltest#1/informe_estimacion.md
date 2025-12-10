# Informe: Estimación de Costos de Equipos para Proyecto de Construcción

data/
  raw/                 (X.csv, Y.csv, Z.csv originales)
  cleaned/             (__cleaned__X.csv, __cleaned__Y.csv, __cleaned__Z.csv)
  processed/           (estimated_equipment_prices.csv, summary_estimates.csv)
  plots/               (equipment_prices_plot.png)


## 1. Explicación del caso
Una empresa de construcción requiere estimar el costo de dos equipos para un proyecto de 36 meses. Los precios de los equipos se componen de las materias primas X, Y y Z:
- **Equipo 1**: 20% X + 80% Y
- **Equipo 2**: 1/3 X + 1/3 Y + 1/3 Z

Referencia del caso: Caso consultoría entregado por la empresa. :contentReference[oaicite:1]{index=1}

## 2. Supuestos
1. Los archivos `X.csv`, `Y.csv`, `Z.csv` contienen series de precios por unidad de cada materia prima.
2. No se incluyen costos adicionales (mano de obra, transporte, impuestos) en la estimación inicial.
3. Se asume que los porcentajes declarados en el enunciado definen la composición del precio base del equipo.
4. Para proyecciones a 36 meses se asume que la volatilidad histórica es representativa del futuro (para Monte Carlo).

## 3. Formas para resolver el caso (y opción adoptada)
Opciones posibles:
- **Determinista directo**: aplicar las fórmulas sobre los precios observados (opción tomada para entregable base).
- **Forecasting**: usar modelos de series temporales (ARIMA, Prophet) para proyectar precios a 36 meses.
- **Simulación**: Monte Carlo para modelar incertidumbre y producir percentiles (p5, p50, p95).
- **Enfoque híbrido**: usar forecasting para la tendencia y Monte Carlo para la incertidumbre residual.

**Opción tomada**: entregar la solución determinista (cálculo directo) + propuestas y scripts para forecasting y Monte Carlo como mejora.

## 4. Resultados del análisis de los datos y los modelos
> Aquí debes pegar los resultados concretos que obtengas al ejecutar `estimation_script.py`:
- Archivo generado: `estimated_equipment_prices.csv`
- Resumen estadístico: `summary_estimates.csv`

### 4.1 Previsualización (ejemplo)
_(Pegar aquí la tabla `head()` de `estimated_equipment_prices.csv` o incrustar la imagen `equipment_prices_plot.png`.)_

### 4.2 Interpretación
- El precio base del Equipo 1 refleja mayor sensibilidad a Y (80%).
- El Equipo 2 es un promedio simple de las 3 materias primas; su comportamiento es más suavizado.

## 5. Futuros ajustes o mejoras
- Incluir **costos adicionales** (logística, impuestos, margen).
- Contratar cláusulas de **fijación de precio** con proveedores para reducir incertidumbre.
- Ejecutar **forecasting** (Prophet/ARIMA) y **Monte Carlo** para producir intervalos de confianza a 36 meses.
- Incluir **escenarios macro** (inflación, precios commodities) para stress testing.

## 6. Apreciaciones y comentarios (opcional)
- Recomendable negociar contratos a plazos o cláusulas CPI para proteger el presupuesto del proyecto frente a subidas de materias primas.
- Documentar claramente las fuentes de datos y las fechas de extracción.

---

## Archivos entregados (sugeridos para el repo)
- `X.csv`, `Y.csv`, `Z.csv` (proporcionados)
- `estimation_script.py` (script principal)
- `forecasting_36m.py` (forecasting con Prophet)
- `montecarlo_36m.py` (simulación Monte Carlo)
- `informe_estimacion.md` (este archivo)
- `equipment_prices_plot.png`, `estimated_equipment_prices.csv`, `summary_estimates.csv` (salidas)

