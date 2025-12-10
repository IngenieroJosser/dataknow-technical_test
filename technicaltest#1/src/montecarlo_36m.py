import pandas as pd
import numpy as np
from pathlib import Path

DATA_DIR = Path('.')
df = pd.read_csv(DATA_DIR / 'estimated_equipment_prices.csv', index_col=0)
# Tomamos último precio observado como punto de partida y volatilidad histórica como sd
n_sim = 10000
horizon_months = 36

results = {}
for equip in ['equip1','equip2']:
    series = df[equip].dropna()
    # daily/periodic returns - approximación por cambios porcentuales
    returns = series.pct_change().dropna()
    mu = returns.mean()
    sigma = returns.std()
    last = series.iloc[-1]
    sims = np.zeros((n_sim, horizon_months))
    for i in range(n_sim):
        prices = [last]
        for t in range(horizon_months):
            shock = np.random.normal(mu, sigma)
            prices.append(prices[-1] * (1 + shock))
        sims[i,:] = prices[1:]
    # guardar percentiles
    pctiles = np.percentile(sims, [5,50,95], axis=0)
    df_pct = pd.DataFrame({
        'month': range(1,horizon_months+1),
        'p5': pctiles[0],
        'p50': pctiles[1],
        'p95': pctiles[2]
    })
    df_pct.to_csv(DATA_DIR / f'montecarlo_{equip}.csv', index=False)
    results[equip] = df_pct
    print(f"Monte Carlo saved: montecarlo_{equip}.csv")
