# S-RU1 shots-on-target engine

Reads `data/ru1_matches.csv`; seed is 2021/2022 and dev scores 2022/2023–2024/2025 (855 stats matches). Arms are GZ and RS; X4 is disabled. The primary line is SOT 7.5 with ladder 6.5/7.5/8.5. FT-only presentation; no halves constants or columns exist. Calibration uses actual minus predicted. Run `python3 league/RU-1Division/engine/sot/run_s_ru1.py dev`.

The dev runner intentionally has no virgin command; virgin evaluation is coordinator-controlled.
