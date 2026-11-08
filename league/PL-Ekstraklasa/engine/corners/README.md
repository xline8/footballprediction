# C-PL corners engine

Reads `data/pl_matches.csv`; seed is 2021/2022 and dev scores 2022/2023–2024/2025 (918 matches). Arms are Gate Zero (X9) and X7. The primary line is corners 9.5 with ladder 8.5/9.5/10.5. Calibration uses actual minus predicted. Run `python3 league/PL-Ekstraklasa/engine/corners/run_c_pl.py dev`.

The dev runner intentionally has no virgin command; virgin evaluation is coordinator-controlled.
