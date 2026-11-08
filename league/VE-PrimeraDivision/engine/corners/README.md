# C-VE engine

Virgin rerun: `python3 run_c_ve.py virgin`. It fits through the first 2026 Clausura date and scores Clausura target rows; missing-target rows are omitted (scored n=90). This run failed calibration, so no predictions or fitted params ship. Frozen halves: 1H 0.4669, 2H 0.5331. The virgin is transitional; the season-end confirmatory read remains outstanding.

`run_c_ve.py` runs the single Gate Zero arm on the 2025 Clausura seed and 2026 Apertura R1–7/R8–13 blocks at lines 7.5, 8.5, and 9.5. It uses the corners-v3 ratings, NB total, possession territorial feature, and zero-valued big-chance feature. The loader asserts the preregistered full-feed windows and `results_dev.json` records the constant-big-chance check.
