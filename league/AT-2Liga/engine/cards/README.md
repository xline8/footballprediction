# K-RU1 cards engine

Reads event-unified `ev_yellow_home + ev_yellow_away` from `data/at2_matches.csv`; seed is 2021/2022 and dev scores 2022/2023–2024/2025 (918 matches). The only arm is Gate Zero; referee/x8 is removed. The primary line is cards 4.5 with ladder 3.5/4.5/5.5. FT-only presentation. Calibration uses actual minus predicted. Run `python3 league/AT-2Liga/engine/cards/run_k_at2.py dev`.

The runner exposes both `dev` and `virgin`; the virgin command refuses arms that did not pass the recorded dev gate.
