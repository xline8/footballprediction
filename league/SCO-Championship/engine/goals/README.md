# G-SCOCH goals engine

Reads `data/sco_championship_matches.csv`; seed is 2021/2022 and dev scores 2022/2023–2024/2025 (540 matches). Arms are Gate Zero, SHRINK, and X2. Calibration uses predicted minus actual. Run `python3 league/SCO-Championship/engine/goals/run_g_scoch.py dev`.

The dev runner intentionally has no virgin command; virgin evaluation is coordinator-controlled.
