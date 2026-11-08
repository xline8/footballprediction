# S-SCOCH shots-on-target engine

Reads `data/sco_championship_matches.csv`; seed is 2021/2022 and dev scores 427 stats matches in 2022/2023–2024/2025. Arms are GZ and RS. The primary line is SOT 7.5 with ladder 6.5/7.5/8.5. FT-only presentation; no halves constants or columns exist. Calibration uses predicted minus actual. Run `python3 league/SCO-Championship/engine/sot/run_s_scoch.py dev`.

The dev runner intentionally has no virgin command; virgin evaluation is coordinator-controlled.
