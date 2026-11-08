# G-DK goals engine

Reads `data/dk_matches.csv`. Dev loads only 2021/2022–2024/2025, using 2021/2022 as seed; virgin reads 2025/2026 only after the recorded dev gate. Arms are `gate_zero`, `shrink`, and `x3`.

```text
python3 league/DK-Superligaen/engine/goals/run_g_dk.py dev
python3 league/DK-Superligaen/engine/goals/run_g_dk.py virgin-metrics
```

Outputs are `results_dev.json`, `results_dev.csv`, and conditional `results_virgin.json`; a passing shipped arm also writes `fitted_params_virgin.json` and `predictions/g_dk_virgin_predictions.csv`.
