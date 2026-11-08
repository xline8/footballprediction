# G-RU1 goals engine

Reads `data/at2_matches.csv`; seed is 2021/2022 and dev scores 2022/2023–2024/2025 (918 matches). Arms are Gate Zero and SHRINK. The X1 blend falls back to goals-only because xG is null on every AT-2Liga row. Calibration uses actual minus predicted. Run `python3 league/AT-2Liga/engine/goals/run_g_at2.py dev`.

The runner exposes both `dev` and `virgin`; the virgin command refuses arms that did not pass the recorded dev gate.
