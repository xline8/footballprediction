# G-CY2 goals engine

This goals-only Dixon–Coles engine reads `league/CY-2Division/data/cy2_matches.csv` and the CY-1 team-season membership JSON for the X2 arm. It uses seed `2021/2022`, scores the expanding walk-forward seasons `2022/2023`–`2024/2025` (pooled n=682), and reserves `2025/2026` for the one-shot virgin evaluation. `2026/2027` is never read by dev or virgin.

The arms are `gate_zero`, `x2`, and `shrink`. Dev writes `results_dev.json` and the summary table `results_dev.csv`. Virgin writes `results_virgin.json`; if an arm ships, it also writes `league/CY-2Division/predictions/g_cy2_virgin_predictions.csv` and `fitted_params_virgin.json`.

From the repository root, rerun with:

```text
~/workspace/footballprediction/.venv/bin/python league/CY-2Division/engine/goals/run_g_cy2.py dev
~/workspace/footballprediction/.venv/bin/python league/CY-2Division/engine/goals/run_g_cy2.py virgin
```

Calibration is reported as actual minus predicted. The virgin half probabilities use the frozen 0.4351 first-half goals share.
