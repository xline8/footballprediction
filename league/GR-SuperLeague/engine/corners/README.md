# C-GR corners engine

Reads `data/gr_matches.csv`; seed is 2021/2022 and dev scores 2022/2023–2024/2025 (716 matches). Arms are Gate Zero (X9) and X7. The primary line is corners 8.5 with ladder 7.5/8.5/9.5. Calibration uses actual minus predicted. Run `python3 league/GR-SuperLeague/engine/corners/run_c_gr.py dev`.

The dev runner intentionally has no virgin command; virgin evaluation is coordinator-controlled.
