# G-AU goals engine

Reads local `data/au_matches.csv`. Dev uses 2021/2022 as seed and scores 2022/2023–2024/2025; virgin reads 2025/2026 only after the recorded Gate Zero dev gate. Arms are `gate_zero`, `shrink`, and `x3`, with the frozen 0.432 half-goals presentation split.

```text
python3 league/AU-ALeague/engine/goals/run_g_au.py dev
python3 league/AU-ALeague/engine/goals/run_g_au.py virgin-metrics
```

Outputs are `results_dev.json`, `results_dev.csv`, and conditional `results_virgin.json`; a passing shipped arm also writes `fitted_params_virgin.json` and `predictions/g_au_virgin_predictions.csv`.
