# League One goals engine

Development-only Dixon-Coles engine. It reads `data/sco_league_one_matches.csv`, warms on 2021/2022, and scores 2022/2023 through 2024/2025 (540 matches) using Gate Zero, SHRINK, and X2. X2 uses only the target season entrants; all fits are goals-only and date-blocked.

Run `python3 league/SCO-LeagueOne/engine/goals/run_g_sco_l1.py dev`. The command writes `results_dev.json` and per-match `results_dev.csv`; it has no virgin command. Calibration is actual − predicted.
