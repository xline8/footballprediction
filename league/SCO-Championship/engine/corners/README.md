# C-SCOCH corners engine

Reads `data/sco_championship_matches.csv`; seed is 2021/2022 and dev scores 427 stats matches in 2022/2023–2024/2025. Gate Zero uses possession-only territorial covariates. The primary line is corners 9.5 with ladder 8.5/9.5/10.5. FT-only presentation. Calibration uses predicted minus actual. Run `python3 league/SCO-Championship/engine/corners/run_c_scoch.py dev`.

The dev runner intentionally has no virgin command; virgin evaluation is coordinator-controlled.
