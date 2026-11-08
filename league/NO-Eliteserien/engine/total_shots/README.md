# T-NO total-shots engine

Reads `../../data/no_matches.csv`; development loads only 2021–2024, with 2021 warm-up, 2022 tuning, and the 2023–2024 gate pool. Arms are A and C; primary line is 26.5 and the presentation-only 1H share is 0.465.

Run from this directory: `python3 run_t_no.py dev`. Outputs are `results_dev.json` and `results_dev.csv`. Virgin commands exist for the coordinator but were not run here.
