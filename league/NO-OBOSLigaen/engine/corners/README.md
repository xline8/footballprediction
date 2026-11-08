# C-NO-OBOS corners engine

Seeded from the NO-Eliteserien corners engine (production
model_corners_v3 pattern via J1). Reads `../../data/no_obos_matches.csv`.
Development loads 2021–2025, season-blocked: target seasons 2022–2025,
training strictly before each target season. Arms are `gate_zero`
(territorial multiplier with the **possession covariate only** —
big_chance does not exist in this feed; prereg) and `plain`
(no-multiplier ablation). Primary line is 10.5. This market is
FT-only (no halves source exists in this league).

Run from this directory: `python3 run_c_obos.py dev` → `results_dev.json`
/ `results_dev.csv`. Virgin (coordinator only, after dev freezes):
`python3 run_c_obos.py virgin --arms gate_zero plain` → `results_virgin.json`,
`fitted_params_virgin.json`, and the shipped arm's predictions CSV.
