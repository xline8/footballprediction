# G-ZA goals engine

Reads `data/za_matches.csv` (regular-season rows only; team identity =
FotMob team id). Seed fit 2021/2022; DEV scores 2022/2023–2024/2025
(690 matches) under the season-blocked walk-forward. Arms are Gate Zero
(production Dixon-Coles pattern, goals-only) and SHRINK. Calibration
uses actual minus predicted. Outputs are `results_dev.json`, summary
CSV, and `predictions_dev.csv`; on a dev pass, `results_virgin.json`,
`fitted_params_virgin.json` and the shipped predictions CSV.
Run `python3 league/ZA-PSL/engine/goals/run_g_za.py dev`
(virgin: `run_g_za.py virgin`, dev-passing arms only).
