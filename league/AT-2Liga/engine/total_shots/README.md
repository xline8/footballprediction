# T-RU1 total-shots engine

Reads `data/at2_matches.csv`; seed is 2021/2022 and dev scores 2022/2023–2024/2025 (855 stats matches). Arms are A, B, and C. The primary line is total shots 18.5 with ladder 17.5/18.5/19.5. FT-only presentation; no halves constant or columns exist. Calibration uses actual minus predicted. Run `python3 league/AT-2Liga/engine/total_shots/run_t_at2.py dev`.

The runner exposes both `dev` and `virgin`; the virgin command refuses arms that did not pass the recorded dev gate.
