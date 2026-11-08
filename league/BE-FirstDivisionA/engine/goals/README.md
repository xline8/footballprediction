# G-BE goals engine

Reads `data/be_matches.csv`. Dev loads only 2021/2022–2024/2025 (n=956), using 2021/2022 as seed; virgin reads 2025/2026 (n=313) only after the recorded dev gate. Arms are `gate_zero`, `shrink`, and `x3`; the xG fallback fires three times. Primary line is OU2.5; frozen halves shares are 0.458/0.542.

```text
python3 league/BE-FirstDivisionA/engine/goals/run_g_be.py dev
python3 league/BE-FirstDivisionA/engine/goals/run_g_be.py virgin-metrics
```

Outputs are `results_dev.json`, `results_dev.csv`, and conditional `results_virgin.json`; a passing shipped arm also writes `fitted_params_virgin.json` and `predictions/g_be_virgin_predictions.csv`.
