# T-NO-OBOS total-shots engine

Seeded from the NO-Eliteserien total-shots engine (shots family via
J1). Reads `../../data/no_obos_matches.csv`. Development loads
2021–2025: 2021 warm-up, 2022 tuning, gate pool 2023–2025. Arms are
A (v1 pattern) and C (E9 trailing-r). Primary line is 20.5. This
market is FT-only (no halves source exists in this league).

Run from this directory: `python3 run_t_obos.py dev` → `results_dev.json`
/ `results_dev.csv` / `fitted_params.json`. Virgin (coordinator only,
after dev freezes): `python3 run_t_obos.py virgin [--export-arm A|C]`.
