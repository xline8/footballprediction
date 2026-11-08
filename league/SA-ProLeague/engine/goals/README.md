# G-SA goals engine
Reads `data/sa_matches.csv`. Dev loads 2021/2022–2024/2025, uses 2021/2022 and 2022/2023 as warm-up, and scores 2023/2024–2024/2025; virgin is 2025/2026 after the recorded dev gate. Arms are `gate_zero`, `shrink`, and `x3`.
Run: `python3 league/SA-ProLeague/engine/goals/run_g_sa.py dev` then `... virgin-metrics`.
Outputs: `results_dev.json/csv`, conditional `results_virgin.json`, `fitted_params_virgin.json`, `predictions/g_sa_virgin_predictions.csv`.
