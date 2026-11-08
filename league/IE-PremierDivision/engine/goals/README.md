# G-IE goals engine
Reads `data/ie_matches.csv`. Dixon-Coles, GOALS-ONLY (IE xG exists only in 2025–2026; prereg freezes the blend out). Dev loads 2021–2025, 2021 as seed, scores 2022–2025; virgin 2026 read once after the dev gate. Arms: `gate_zero`, `shrink` (identical in practice — season-blocked fits give promoted teams 0 prior in-league matches, so shrink never bites). Prereg: `prereg/PREREG_G_IE.md` (1X2 LL/RPS + OU 2.5; halves constant 0.4439).
Run: `python3 league/IE-PremierDivision/engine/goals/run_g_ie.py dev` then `... virgin-metrics` / `... virgin-predict --arm gate_zero`.
Outputs: `results_dev.json/csv`, `results_virgin.json`, `fitted_params_virgin.json`, `predictions/g_ie_virgin_predictions.csv`.
