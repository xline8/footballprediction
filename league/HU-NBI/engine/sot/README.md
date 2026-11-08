# S-HU-NBI shots-on-target engine

DEV-only copied SOT mechanics. The loader maps HU `total_shots_h/a` and `sot_h/a`, uses numeric HU team IDs, and hard-allows only 2021/2022 through 2024/2025. Arms are GZ and RS. Frozen line: 8.5; 2021/2022 is warm-up and the next three seasons are scored. Stats markets are FT-only.

Run `python3 run_s_obos.py`. Outputs are `results_dev.json` and per-arm `dev_predictions_GZ.csv` / `dev_predictions_RS.csv`.

