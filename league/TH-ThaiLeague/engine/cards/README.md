# K-TH cards engine

Reads stats-feed `yellow_cards_home + yellow_cards_away` from `data/th_matches.csv`; 2022/2023 is warm-up and DEV scores 2023/2024–2024/2025 (480 rows). Gate Zero only; primary line 4.5, ladder 3.5/4.5/5.5. Outputs are `results_dev.json`, summary CSV, and `predictions_dev.csv`. Run `python3 league/TH-ThaiLeague/engine/cards/run_k_th.py dev`.

DEV only; virgin is forbidden in Phase B.
