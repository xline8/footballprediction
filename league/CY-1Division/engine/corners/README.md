# C-CY corners engine

Reads `data/cy_matches.csv`; 2021/2022 is the seed and DEV scores
2022/2023–2024/2025 (765 stats rows). Production `model_corners_v3`
pattern (J1 construction); the gamma/beta/r fitting objective is at
the primary line 9.5, ladder 8.5/9.5/10.5. Arm is Gate Zero
(possession-only territorial covariate; big chance is absent). Calibration uses actual minus
predicted. Outputs are `results_dev.json` and per-match `results_dev.csv`.
Run `python3 league/CY-1Division/engine/corners/run_c_cy.py dev`.
