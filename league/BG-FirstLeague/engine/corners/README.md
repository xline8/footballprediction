# C-ZA corners engine

Reads `data/za_matches.csv`; 2022/2023 is the seed and DEV scores
2023/2024–2024/2025 (448 stats rows). Production `model_corners_v3`
pattern (J1 construction); the gamma/beta/r fitting objective is at
the primary line 8.5, ladder 7.5/8.5/9.5. Arms are Gate Zero
(possession + big chance) and X7 (touches in opponent box); missing
X7 history is inactive, never filled. Calibration uses actual minus
predicted. Outputs are `results_dev.json`, summary CSV, and
`predictions_dev.csv`; virgin adds `results_virgin.json`,
`fitted_params_virgin.json`, `predictions_virgin_all.csv` and, on a
pass, `predictions/c_za_virgin_predictions.csv` (FT ladder + 1H/2H
presentation via the frozen corners constant 0.4679).
Run `python3 league/ZA-PSL/engine/corners/run_c_za.py dev`
(virgin: `run_c_za.py virgin`, dev-passing arms only).
