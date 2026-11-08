# G-HU-NBI goals engine

DEV-only expanding Dixon–Coles engine copied from the source league mechanics. HU rows are adapted from `data/hu_nbi.csv`; xG fields are unavailable, so goals-only observations are used. Arms are GZ and SHR; the SHR arm applies the copied low-history shrink adjustment. Frozen line: 2.5. Base season is 2021/2022; 2022/2023–2024/2025 are scored. 2025/2026 and 2026/2027 are hard-blocked. HU halves constant is 0.4471; this DEV output is FT-only.

Run `python3 run_g_obos.py`. Outputs are `results_dev.json` and `dev_predictions_GZ.csv` / `dev_predictions_SHR.csv`.

