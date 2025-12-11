#!/usr/bin/env python3
"""
estimation_script.py
Procesa X.csv, Y.csv, Z.csv con diferentes formatos de fecha, delimitadores
y formatos numéricos. Calcula:

Equipo 1 = 0.2 * X + 0.8 * Y
Equipo 2 = (X + Y + Z) / 3

Ahora organiza:
- data/raw:         X.csv, Y.csv, Z.csv originales
- data/cleaned:     __cleaned__X.csv, __cleaned__Y.csv, __cleaned__Z.csv
- data/processed:   estimated_equipment_prices.csv, summary_estimates.csv
- data/plots:       equipment_prices_plot.png
"""

import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt


ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"

RAW_DIR = DATA_DIR / "raw"
CLEAN_DIR = DATA_DIR / "cleaned"
PROCESSED_DIR = DATA_DIR / "processed"
PLOTS_DIR = DATA_DIR / "plots"


# ---------------------------------------------------------------------------
# Crear carpetas si no existen
# ---------------------------------------------------------------------------
for d in [RAW_DIR, CLEAN_DIR, PROCESSED_DIR, PLOTS_DIR]:
    d.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Robust CSV Reader
# ---------------------------------------------------------------------------
def robust_read_csv(path: Path) -> pd.DataFrame:
    """
    Lector robusto:
    - limpia BOM
    - prueba múltiples delimitadores
    - convierte comas decimales
    - guarda copia limpia en data/cleaned/
    """
    raw = path.read_text(encoding="utf-8", errors="ignore").replace("\ufeff", "")

    # Nuevo destino: carpeta cleaned
    cleaned_path = CLEAN_DIR / f"__cleaned__{path.name}"
    cleaned_path.write_text(raw, encoding="utf-8")

    df = None
    for sep in [None, ";", ",", "\t", "|"]:
        try:
            df = pd.read_csv(cleaned_path, sep=sep)
            if not df.empty:
                break
        except Exception:
            continue

    if df is None or df.empty:
        raise ValueError(f"No se pudo leer el archivo: {path}")

    df.columns = [c.strip().replace("\ufeff", "") for c in df.columns]

    # Normalización de números
    for col in df.columns:
      if any(k in col.lower() for k in ["date", "fecha", "time"]):
          continue

      ser = (
          df[col]
          .astype(str)
          .str.strip()
          .str.replace(".", "", regex=False)     # eliminar separador de miles europeo
          .str.replace(",", ".", regex=False)    # convertir coma decimal
      )

      # Conversión estricta: forzamos numérico, lo inválido → NaN
      df[col] = pd.to_numeric(ser, errors="coerce")


    return df


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def first_numeric_col(df: pd.DataFrame):
    for c in df.columns:
        if pd.api.types.is_numeric_dtype(df[c]):
            return c
    raise ValueError("No numeric column found")


def maybe_parse_date(df: pd.DataFrame):
    for c in df.columns:
        if any(k in c.lower() for k in ["date", "fecha", "time"]):
            df[c] = pd.to_datetime(df[c], errors="coerce", dayfirst=True)
            df = df.dropna(subset=[c])
            df = df.sort_values(c).set_index(c)
            return df
    return df


# ---------------------------------------------------------------------------
# MAIN PIPELINE
# ---------------------------------------------------------------------------
def main():
    # Archivos originales deben estar en data/raw/
    paths = {
        "X": RAW_DIR / "X.csv",
        "Y": RAW_DIR / "Y.csv",
        "Z": RAW_DIR / "Z.csv",
    }

    for name, p in paths.items():
        if not p.exists():
            raise FileNotFoundError(
                f"No se encontró {name}.csv en {RAW_DIR}. Colócalo ahí."
            )

    # Leer y limpiar
    X = robust_read_csv(paths["X"])
    Y = robust_read_csv(paths["Y"])
    Z = robust_read_csv(paths["Z"])

    X = maybe_parse_date(X)
    Y = maybe_parse_date(Y)
    Z = maybe_parse_date(Z)

    x_col = first_numeric_col(X)
    y_col = first_numeric_col(Y)
    z_col = first_numeric_col(Z)

    Xs = X[x_col].rename("X")
    Ys = Y[y_col].rename("Y")
    Zs = Z[z_col].rename("Z")

    # Combinar por índice si son fechas
    try:
        combined = pd.concat([Xs, Ys, Zs], axis=1)
    except Exception:
        combined = pd.DataFrame({
            "X": Xs.reset_index(drop=True),
            "Y": Ys.reset_index(drop=True),
            "Z": Zs.reset_index(drop=True),
        })

    # Cálculos
    combined["equip1"] = 0.2 * combined["X"] + 0.8 * combined["Y"]
    combined["equip2"] = (combined["X"] + combined["Y"] + combined["Z"]) / 3.0

    summary = combined.describe()

    # Guardar outputs en carpetas organizadas
    combined.to_csv(PROCESSED_DIR / "estimated_equipment_prices.csv")
    summary.to_csv(PROCESSED_DIR / "summary_estimates.csv")

    # Gráfica
    plt.figure(figsize=(10, 5))
    combined[["equip1", "equip2"]].plot(title="Estimated Equipment Base Prices")
    plt.xlabel("Index (fecha o posición)")
    plt.ylabel("Precio")
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / "equipment_prices_plot.png")
    plt.close()

    print("\n=== OUTPUTS GENERADOS ===")
    print(f" Limpios:      {CLEAN_DIR}")
    print(f" Procesados:   {PROCESSED_DIR}")
    print(f" Gráficas:     {PLOTS_DIR}")
    print("==========================\n")


if __name__ == "__main__":
    main()
