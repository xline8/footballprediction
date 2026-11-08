# G-ENGL1 goals engine
Reads `data/engl1_matches.csv`. Dev loads only 2021/2022–2024/2025, using 2021/2022 as seed; virgin is reserved for later. Arms are `gate_zero`, `shrink`, and `x2`, with the preregistered League One Championship/L2 mover offsets. Prereg: `PREREG_G_ENGL1.md` (halves constant 0.4425).
Run: `python3 league/ENG-LeagueOne/engine/goals/run_g_engl1.py dev`.
Outputs: `results_dev.json/csv`.
