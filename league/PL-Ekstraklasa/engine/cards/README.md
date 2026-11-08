# K-PL cards engine

Reads unified `yellow_home + yellow_away` and `cards_source` from `data/pl_matches.csv`; seed is 2021/2022 and dev scores 2022/2023–2024/2025 (918 matches). Arms are Gate Zero and X8 referee adjustment. The primary line is cards 3.5 with ladder 2.5/3.5/4.5. Calibration uses actual minus predicted. Run `python3 league/PL-Ekstraklasa/engine/cards/run_k_pl.py dev`.

The dev runner intentionally has no virgin command; virgin evaluation is coordinator-controlled.
