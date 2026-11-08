# G-DE3 goals engine

Reads `data/de3_matches.csv`. This is goals-only Dixon–Coles: no xG blend path. Dev uses the 2021/2022 seed and scores 2022/2023–2024/2025 (n=1,140); virgin 2025/2026 is conditional on the frozen gate. Arms are `gate_zero` and `shrink`. Primary line is OU2.5; frozen halves shares are 0.445/0.555.

```text
python3 league/DE-3Liga/engine/goals/run_g_de3.py dev
python3 league/DE-3Liga/engine/goals/run_g_de3.py virgin-metrics --arms gate_zero shrink
```

Outputs are `results_dev.json`, `results_dev.csv`, and conditional `results_virgin.json`; a shipped arm also writes `fitted_params_virgin.json` and `predictions/g_de3_virgin_predictions.csv`.
