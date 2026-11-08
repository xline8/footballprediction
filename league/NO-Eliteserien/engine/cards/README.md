# K-NO cards engine

Reads `../../data/no_matches.csv`; development loads only 2021–2024, with 2021 warm-up and 2022–2024 scored. The only arm is `gate_zero`; no referee arm is exposed. Primary line is 2.5 and the presentation-only 1H share is 0.317.

Run from this directory: `python3 run_k_no.py dev`. Outputs are `results_dev.json` and `results_dev.csv`. Virgin commands exist for the coordinator but were not run here.
