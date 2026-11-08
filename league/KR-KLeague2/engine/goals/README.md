# KR2 goals engine

Inputs are the regular-phase rows in `data/kr2_matches.csv`; 2026 is never loaded by dev or virgin. Outputs are `results_dev.json/csv`, `predictions_dev.csv`, and virgin artifacts when an arm passes. Run `python3 league/KR-KLeague2/engine/goals/run_g_kr2.py dev` or `virgin --arms gate_zero,shrink,x2`.
