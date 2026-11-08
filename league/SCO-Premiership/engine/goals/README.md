# G-SCO goals engine
Reads `data/sco_matches.csv`. Dev loads only 2021/2022–2024/2025, using 2021/2022 as seed; virgin reads 2025/2026 only after the recorded dev gate. Arms are `gate_zero`, `shrink`, and `x3`. Prereg: `prereg/PREREG_G_SCO.md` (primary OU 2.5 + 1X2 LL/RPS; halves constant 0.4405).
Run: `python3 league/SCO-Premiership/engine/goals/run_g_sco.py dev` then `... virgin-metrics`.
Outputs: `results_dev.json/csv`, conditional `results_virgin.json`, `fitted_params_virgin.json`, `predictions/g_sco_virgin_predictions.csv`.
