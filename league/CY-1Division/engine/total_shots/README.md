# T-CY total-shots engine

Reads `data/cy_matches.csv`. Shots family: arm A =
v1 pattern (ratings + NB + naive ensemble), B = v2 (+ level layer),
C = E9 (NB r from a trailing 200-match window). Seed/tuning
2021/2022; DEV scores 2022/2023–2024/2025 (765 stats rows). Primary
line 18.5, ladder 17.5/18.5/19.5. Calibration uses actual minus
predicted. Outputs are `results_dev.json`, per-match `results_dev.csv`
and `fitted_params.json`. Run `python3 league/CY-1Division/engine/total_shots/run_t_cy.py dev`.
