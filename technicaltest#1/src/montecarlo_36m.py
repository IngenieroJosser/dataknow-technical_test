import pandas as pd
import numpy as np
from pathlib import Path


# =============================================================================
# CONFIGURACIÓN DE RUTAS DEL PROYECTO
# =============================================================================
ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
PROCESSED_DIR = DATA_DIR / "processed"
OUTPUT_MC_DIR = PROCESSED_DIR / "montecarlo"

# Crear directorio si no existe
OUTPUT_MC_DIR.mkdir(parents=True, exist_ok=True)

# Archivo fuente
FILE_PATH = PROCESSED_DIR / "estimated_equipment_prices.csv"

if not FILE_PATH.exists():
    raise FileNotFoundError(
        f"No se encontró el archivo estimado en: {FILE_PATH}\n"
        f"Asegúrate de ejecutar primero estimation_script.py"
    )


# =============================================================================
# CARGA DE DATOS
# =============================================================================
df = pd.read_csv(FILE_PATH, index_col=0)

n_sim = 10000
horizon_months = 36

results = {}

print("\n=== EJECUTANDO SIMULACIÓN MONTE CARLO ===\n")

for equip in ["equip1", "equip2"]:

    if equip not in df.columns:
        print(f"Advertencia: {equip} no está en el dataframe. Se omite.")
        continue

    print(f"• Simulando: {equip}")

    series = df[equip].dropna()

    # Cálculo de retornos históricos
    returns = series.pct_change().dropna()

    mu = returns.mean()        # retorno promedio
    sigma = returns.std()      # volatilidad histórica
    last = series.iloc[-1]     # último valor observable

    sims = np.zeros((n_sim, horizon_months))

    for i in range(n_sim):
        prices = [last]
        for t in range(horizon_months):
            shock = np.random.normal(mu, sigma)
            prices.append(prices[-1] * (1 + shock))
        sims[i, :] = prices[1:]

    # Percentiles 5, 50 (mediana), 95
    pctiles = np.percentile(sims, [5, 50, 95], axis=0)

    df_pct = pd.DataFrame({
        "month": range(1, horizon_months + 1),
        "p5": pctiles[0],
        "p50": pctiles[1],
        "p95": pctiles[2]
    })

    out_file = OUTPUT_MC_DIR / f"montecarlo_{equip}.csv"
    df_pct.to_csv(out_file, index=False)

    results[equip] = df_pct

    print(f"  Archivo generado → {out_file}")


print("\n=== MONTE CARLO COMPLETADO ===")
print(f"Resultados guardados en: {OUTPUT_MC_DIR}\n")
