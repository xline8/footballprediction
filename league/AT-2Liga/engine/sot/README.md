# S-RU1 shots-on-target engine

Reads `data/at2_matches.csv`; seed is 2021/2022 and dev scores 2022/2023–2024/2025 (855 stats matches). Arms are GZ and RS; X4 is disabled. The primary line is SOT 8.5 with ladder 7.5/8.5/9.5. FT-only presentation; no halves constants or columns exist. Calibration uses actual minus predicted. Run `python3 league/AT-2Liga/engine/sot/run_s_at2.py dev`.

The runner exposes both `dev` and `virgin`; the virgin command refuses arms that did not pass the recorded dev gate.
