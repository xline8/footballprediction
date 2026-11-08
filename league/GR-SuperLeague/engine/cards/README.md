# K-GR cards engine

Reads unified `yellow_home + yellow_away` from `data/gr_matches.csv`; seed is 2021/2022 and dev scores 2022/2023–2024/2025 (716 matches). The only arm is Gate Zero; referee covariates are not used. The primary line is cards 4.5 with ladder 3.5/4.5/5.5. Calibration uses actual minus predicted. Run `python3 league/GR-SuperLeague/engine/cards/run_k_gr.py dev`.

The dev runner intentionally has no virgin command; virgin evaluation is coordinator-controlled.
