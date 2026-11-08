# G-DE2 goals engine

Reads `data/de2_matches.csv`. Dev loads only 2021/2022–2024/2025 (n=918), using 2021/2022 as seed; virgin reads 2025/2026 (n=306) only after the recorded dev gate. Arms are `gate_zero`, `shrink`, `x2`, and `x3`; xG is present in every match. Primary line is OU2.5; the frozen halves shares are 0.450/0.550.

```text
python3 league/DE-2Bundesliga/engine/goals/run_g_de2.py dev
python3 league/DE-2Bundesliga/engine/goals/run_g_de2.py virgin-metrics
```

Outputs are `results_dev.json`, `results_dev.csv`, and conditional `results_virgin.json`; a passing shipped arm also writes `fitted_params_virgin.json` and `predictions/g_de2_virgin_predictions.csv`.
