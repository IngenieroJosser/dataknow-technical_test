import pandas as pd
from prophet import Prophet
from pathlib import Path


# CONFIGURACIÓN DE RUTAS DEL PROYECTO
ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
PROCESSED_DIR = DATA_DIR / "processed"


# CARGA DEL DATASET PROCESADO
FILE_PATH = PROCESSED_DIR / "estimated_equipment_prices.csv"

if not FILE_PATH.exists():
    raise FileNotFoundError(
        f"No se encontró el archivo estimado en: {FILE_PATH}\n"
        f"Asegúrate de ejecutar primero estimation_script.py"
    )

df = pd.read_csv(FILE_PATH, index_col=0)


# CREACIÓN DEL ÍNDICE TEMPORAL PARA PROPHET

# Si el índice ya es datetime → usarlo
if pd.api.types.is_datetime64_any_dtype(df.index):
    ds_index = df.index
else:
    # Crear fechas diarias artificiales (MEJOR si tu serie no trae fechas)
    ds_index = pd.date_range(
        start=pd.Timestamp.today().normalize(),
        periods=len(df),
        freq="D"
    )


# FORECASTING PARA EQUIP1 Y EQUIP2
OUTPUT_FORECAST_DIR = PROCESSED_DIR / "forecast"
OUTPUT_FORECAST_DIR.mkdir(parents=True, exist_ok=True)

print("\n=== GENERANDO FORECAST PARA EQUIPOS ===\n")

for equip in ["equip1", "equip2"]:
    if equip not in df.columns:
        print(f"Advertencia: {equip} no está en el dataframe. Se omite.")
        continue

    print(f"• Entrenando modelo Prophet para: {equip}")

    # Prophet requiere columnas específicas: ds (fecha), y (valor)
    temp = pd.DataFrame({
        "ds": ds_index,
        "y": df[equip].values
    })

    m = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=False,
        daily_seasonality=False
    )

    m.fit(temp)

    # Forecast 36 meses → frecuencia mensual
    future = m.make_future_dataframe(periods=36, freq="M")
    forecast = m.predict(future)

    # Exportar forecast
    out_file = OUTPUT_FORECAST_DIR / f"forecast_{equip}.csv"
    forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]].to_csv(out_file, index=False)

    print(f"  Forecast generado → {out_file}")


print("\n=== FORECAST COMPLETADO ===")
print(f"Archivos generados en: {OUTPUT_FORECAST_DIR}\n")
