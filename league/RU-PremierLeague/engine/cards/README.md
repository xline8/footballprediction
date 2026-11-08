# K-RU cards engine

Reads event-unified `ev_yellow_home + ev_yellow_away` from `data/ru_matches.csv`; seed is 2021/2022 and dev scores 2022/2023–2024/2025 (720 matches). The only arm is Gate Zero; referee/x8 is removed. The primary line is cards 4.5 with ladder 3.5/4.5/5.5. Calibration uses actual minus predicted. Run `python3 league/RU-PremierLeague/engine/cards/run_k_ru.py dev`.

The dev runner intentionally has no virgin command; virgin evaluation is coordinator-controlled.
