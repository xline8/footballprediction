# S-CY shots-on-target engine

Reads `data/cy_matches.csv`. Warm-up 2021/2022 updates state, never scored; DEV scores
2022/2023–2024/2025 (765 stats rows). Primary line 8.5, ladder
7.5/8.5/9.5. Arms are Gate Zero (GZ) and RS (Beta-Binomial prior
P 200 → 20,000). Calibration uses actual minus predicted. Outputs are
`results_dev.json` and per-match `results_dev.csv`.
Run `python3 league/CY-1Division/engine/sot/run_s_cy.py dev`.
