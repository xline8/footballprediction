# S-GR shots-on-target engine

Reads `data/gr_matches.csv`; seed is 2021/2022 and dev scores 2022/2023–2024/2025 (716 matches). Arms are GZ and RS; X4 and X6 are disabled. The primary line is SOT 8.5 with ladder 7.5/8.5/9.5. Calibration uses actual minus predicted. Run `python3 league/GR-SuperLeague/engine/sot/run_s_gr.py dev`.

The dev runner intentionally has no virgin command; virgin evaluation is coordinator-controlled.
