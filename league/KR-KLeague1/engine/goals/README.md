# G-KR goals engine

Reads `data/kr_matches.csv`. Dev loads only 2021–2024, using 2021 as seed; virgin reads 2025 only after the recorded dev gate. Arms are `gate_zero`, `shrink`, and `x2`.

```text
python3 league/KR-KLeague1/engine/goals/run_g_kr.py dev
python3 league/KR-KLeague1/engine/goals/run_g_kr.py virgin-metrics
```

Outputs are `results_dev.json` and `results_dev.csv`; virgin is deliberately unread because Gate Zero fails its dev gate. A passing shipped arm would write `fitted_params_virgin.json` and `predictions/g_kr_virgin_predictions.csv`.
