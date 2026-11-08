# K-SCOCH cards engine

Reads unified `yellow_home + yellow_away` from `data/sco_championship_matches.csv`; seed is 2021/2022 and dev scores 540 matches in 2022/2023–2024/2025. The only arm is Gate Zero. The primary line is cards 3.5 with ladder 2.5/3.5/4.5. FT-only presentation. Calibration uses predicted minus actual. Run `python3 league/SCO-Championship/engine/cards/run_k_scoch.py dev`.

The dev runner intentionally has no virgin command; virgin evaluation is coordinator-controlled.
