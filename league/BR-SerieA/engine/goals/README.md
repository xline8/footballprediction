# G-BR goals engine

Reads `league/BR-SerieA/data/br_matches.csv`. Dev uses 2021 warm-up and scores 2022–2024; virgin is 2025 after the recorded dev gate. Arms are `gate_zero`, `shrink`, `x2`, and `x3`.

```text
python3 league/BR-SerieA/engine/goals/run_g_br.py dev
python3 league/BR-SerieA/engine/goals/run_g_br.py virgin-metrics
```

Outputs are `results_dev.json`, `results_dev.csv`, and conditional `results_virgin.json`; a passing shipped arm also writes `fitted_params_virgin.json` and `predictions/g_br_virgin_predictions.csv`.
