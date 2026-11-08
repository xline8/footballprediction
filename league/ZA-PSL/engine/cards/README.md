# K-ZA cards engine

Reads `data/za_matches.csv`. Target = stats-feed `yellow_cards`
(frozen: the dev- and virgin-era event feeds publish no plain-yellow
events, so no event-unified target exists — see prereg). Production
`model_cards.py` pattern; Gate Zero only (referee feature X8
dropped). Seed 2022/2023; DEV scores 2023/2024–2024/2025 (447 rows
with the target). Primary line 3.5, ladder 2.5/3.5/4.5. Calibration
uses actual minus predicted. Outputs are `results_dev.json`, summary
CSV, and `predictions_dev.csv`.
Run `python3 league/ZA-PSL/engine/cards/run_k_za.py dev`.
