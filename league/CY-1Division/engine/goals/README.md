# G-CY goals engine

Reads `data/cy_matches.csv` (regular-season rows only; team identity =
team id). Seed fit 2021/2022; DEV scores 2022/2023–2024/2025
(776 matches) under the season-blocked walk-forward. Arms are Gate Zero
(production Dixon-Coles pattern, goals-only) and SHRINK. Calibration
uses actual minus predicted. Outputs are `results_dev.json` and per-match
`results_dev.csv`. Run `python3 league/CY-1Division/engine/goals/run_g_cy.py dev`.
