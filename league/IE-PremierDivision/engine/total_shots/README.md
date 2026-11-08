# T-IE total-shots engine
Reads `data/ie_matches.csv`; A/B/C shots-family arms, ladder 23.5/24.5/25.5 (primary 24.5), frozen 1H share 0.4600. Warm-up 2022, tuning season 2023, scores 2023–2025; virgin 2026. Prereg: `prereg/PREREG_T_IE.md`.
Run: `python3 league/IE-PremierDivision/engine/total_shots/run_t_ie.py dev` then `... virgin`.
Outputs: `results_dev.json/csv`, `results_virgin.json`, `fitted_params.json` (no virgin predictions — nothing shipped).
