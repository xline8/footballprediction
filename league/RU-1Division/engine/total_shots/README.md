# T-RU1 total-shots engine

Reads `data/ru1_matches.csv`; seed is 2021/2022 and dev scores 2022/2023–2024/2025 (855 stats matches). Arms are A, B, and C. The primary line is total shots 15.5 with ladder 14.5/15.5/16.5. FT-only presentation; no halves constant or columns exist. Calibration uses actual minus predicted. Run `python3 league/RU-1Division/engine/total_shots/run_t_ru1.py dev`.

The dev runner intentionally has no virgin command; virgin evaluation is coordinator-controlled.
