# G-SE goals engine

Reads `data/se_matches.csv`. Dev loads only 2021–2024, using 2021 as seed; virgin reads 2025 only after the recorded dev gate. Arms are `gate_zero`, `shrink`, and `x3`.

```text
python3 league/SE-Allsvenskan/engine/goals/run_g_se.py dev
python3 league/SE-Allsvenskan/engine/goals/run_g_se.py virgin-metrics
```

Outputs are `results_dev.json`, `results_dev.csv`, and conditional `results_virgin.json`; a passing shipped arm also writes `fitted_params_virgin.json` and `predictions/g_se_virgin_predictions.csv`.
