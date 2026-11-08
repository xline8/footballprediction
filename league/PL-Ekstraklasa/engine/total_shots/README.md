# T-PL total-shots engine

Reads `data/pl_matches.csv`; seed is 2021/2022 and dev scores 2022/2023–2024/2025 (918 matches). Arms are A, B, and C. The primary line is total shots 25.5 with ladder 24.5/25.5/26.5; frozen half split is 0.4592/0.5408. Calibration uses actual minus predicted. Run `python3 league/PL-Ekstraklasa/engine/total_shots/run_t_pl.py dev`.

The dev runner intentionally has no virgin command; virgin evaluation is coordinator-controlled.
