# T-VE engine

Virgin rerun: `python3 run_t_ve.py virgin`. It reruns DEV, then reads only dev-passing arms on 2026 Clausura, omitting the missing target (scored n=90). This run failed, so no predictions or fitted params ship. Frozen halves: 1H 0.4662, 2H 0.5338. The virgin is transitional; the season-end confirmatory read remains outstanding.

`run_t_ve.py dev` runs arms A (v1), B (v2 level layer), and C (E9 trailing dispersion) on the 2025 Clausura seed and 2026 Apertura R1–7/R8–13 blocks. Primary line is 24.5 with secondary lines 23.5 and 25.5. `dev` writes only DEV results and fitted DEV tuning parameters; `virgin` additionally reads 2026 Clausura and writes `results_virgin.json`.
