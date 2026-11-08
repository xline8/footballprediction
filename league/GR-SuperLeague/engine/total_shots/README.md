# T-GR total-shots engine

Reads `data/gr_matches.csv`; the 2021/2022 total-shots feed is excluded from every fit, state, window, rating, r estimate, and baseline. Dev scores 2022/2023–2024/2025 (716 matches). Arms are A, B, and C. The primary line is total shots 22.5 with ladder 21.5/22.5/23.5; frozen half split is 0.4611/0.5389. Calibration uses actual minus predicted. Run `python3 league/GR-SuperLeague/engine/total_shots/run_t_gr.py dev`.

The dev runner intentionally has no virgin command; virgin evaluation is coordinator-controlled.
