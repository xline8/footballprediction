# C-IE corners engine
Reads `data/ie_matches.csv`; primary line 9.5, frozen 1H share 0.4762. Warm-up 2022, scores 2023–2025; virgin 2026. Arms: gate_zero (X9 possession + big_chance), x7 (box touches). Prereg: `prereg/PREREG_C_IE.md`.
Run: `python3 league/IE-PremierDivision/engine/corners/run_c_ie.py dev` then `... virgin --arms gate_zero x7`.
Outputs: `results_dev.json/csv`, `results_virgin.json`, `fitted_params_virgin.json`, `predictions/c_ie_virgin_predictions.csv`.
