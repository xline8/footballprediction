# G-CO goals engine

The engine reads `league/CO-PrimeraB/data/co_primerab_matches.csv`, using the
preregistered Dixon–Coles goals model (14 sweeps, damping 0.7, +0.25
smoothing, 270-day half-life, and rho grid `0.0, -0.05, -0.10, -0.15`).
Arms are `gate_zero`, `shrink`, and mover-down `x2`. It also reports the
trailing-10 naive baseline and climatology.

From the repository root:

```bash
python3 league/CO-PrimeraB/data/build_data.py
python3 league/CO-PrimeraB/analysis/make_charts.py
cd league/CO-PrimeraB/engine/goals
python3 run_g_co.py dev
python3 run_g_co.py virgin --arms gate_zero,shrink,x2
python3 run_g_co.py predict --arm gate_zero
```

Development uses seasons 2021–2024 and evaluates 2022–2024. Virgin and
prediction use 2021–2025 only, with 2025 as target. Outputs include the dev
JSON/CSV, virgin results, and `league/CO-PrimeraB/predictions/g_co_virgin_predictions.csv`.
