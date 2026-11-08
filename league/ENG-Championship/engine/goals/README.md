# G-ENGCH goals engine
Reads `data/engch_matches.csv`. Dev loads only 2021/2022–2024/2025, using 2021/2022 as seed; virgin is reserved for later. Arms are `gate_zero`, `shrink`, and `x2`, with the preregistered Championship PL/L1 mover offsets. Prereg: `PREREG_G_ENGCH.md` (halves constant 0.4453).
Run: `python3 league/ENG-Championship/engine/goals/run_g_engch.py dev`.
Outputs: `results_dev.json/csv`.
