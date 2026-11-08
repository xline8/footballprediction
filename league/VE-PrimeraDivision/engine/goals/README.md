# G-VE engine

Virgin rerun: `python3 run_g_ve.py virgin`. It reads 2025 regular only for dev-passing arms and writes `results_virgin.json`; a PASS would write predictions and fitted params. This run failed calibration. Frozen halves: 1H 0.4478, 2H 0.5522.

`run_g_ve.py` runs the frozen DEV (regular 2021–2024 VE rows, Dixon–Coles with the preregistered decay, smoothing, rho grid, and MAXG=10, writing `results_dev.json`) and, with argument `virgin`, scores dev-passing arms on 2025 regular and writes `results_virgin.json`. Gate Zero is the reference fit; SHRINK scales attack/defence by prior in-league match count / 6 when fewer than six prior matches exist.
