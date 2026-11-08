# T-SCOCH total-shots engine

Reads `data/sco_championship_matches.csv`; seed is 2021/2022 and dev scores 2022/2023–2024/2025 (427 stats matches). Arms are A, B, and C. The primary line is total shots 15.5 with ladder 14.5/15.5/16.5. FT-only presentation; no halves columns exist. Calibration uses predicted minus actual. Run `python3 league/SCO-Championship/engine/total_shots/run_t_scoch.py dev`.

The dev runner intentionally has no virgin command; virgin evaluation is coordinator-controlled.
