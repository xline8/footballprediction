# G-GE goals engine

The engine reads `league/GE-Erovnuli/data/ge_matches.csv`, using only match
goals. It fits the preregistered Dixon–Coles model with 14 multiplicative
sweeps, damping 0.7, +0.25 smoothing, a 270-day time-decay half-life, and a
rho grid of `0.0, -0.05, -0.10, -0.15`. The available arms are `gate_zero`
and prediction-time `shrink`.

Run from the repository root:

```bash
python3 league/GE-Erovnuli/engine/goals/run_g_ge.py dev
python3 league/GE-Erovnuli/engine/goals/run_g_ge.py virgin --arms gate_zero,shrink
python3 league/GE-Erovnuli/engine/goals/run_g_ge.py predict --arm gate_zero
```

`dev` reads only seasons 2021–2024 and writes `results_dev.json` and
`results_dev.csv`. `virgin` evaluates the requested arms on season 2025 and
writes `results_virgin.json` plus `fitted_params_virgin.json`; it does not
write predictions. `predict` fits on matches before the first 2025 match and
writes `league/GE-Erovnuli/predictions/g_ge_virgin_predictions.csv` with the
full-time and preregistered 1H/2H over-goals probabilities.
