# T-ZA total-shots engine

Reads `data/za_matches.csv`. Shots family (J1 construction): arm A =
v1 pattern (ratings + NB + naive ensemble), B = v2 (+ level layer),
C = E9 (NB r from a trailing 200-match window). Seed/tuning
2022/2023; DEV scores 2023/2024–2024/2025 (448 stats rows). Primary
line 21.5, ladder 20.5/21.5/22.5. Calibration uses actual minus
predicted. Outputs are `results_dev.json`, summary CSV,
`predictions_dev.csv` and `fitted_params.json`; virgin adds
`results_virgin.json`, `fitted_params_virgin.json`,
`predictions_virgin.csv` and, on a pass,
`predictions/t_za_virgin_predictions.csv`.
Run `python3 league/ZA-PSL/engine/total_shots/run_t_za.py dev`;
virgin via `from run_t_za import virgin; virgin()` (refuses arms
that did not pass the recorded dev gate).
