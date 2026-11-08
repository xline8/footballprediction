# G-RU1 goals engine

Reads `data/ru1_matches.csv`; seed is 2021/2022 and dev scores 2022/2023–2024/2025 (918 matches). Arms are Gate Zero and SHRINK. The X1 blend falls back to goals-only because xG is null on every RU-1Division row. Calibration uses actual minus predicted. Run `python3 league/RU-1Division/engine/goals/run_g_ru1.py dev`.

The dev runner intentionally has no virgin command; virgin evaluation is coordinator-controlled.
