# K-PE cards engine

Loads only regular, non-awarded blocks from 2023 onward and uses the event-unified yellow target `ev_yellow_inc2nd_home + ev_yellow_inc2nd_away`. DEV warms on 2023 Apertura and scores 2023 Clausura through 2024 Clausura; virgin code targets both 2025 blocks but was not run.

Run `python3 run_k_pe.py dev`. Outputs are `results_dev.json` and `results_dev.csv`. Primary line is 4.5, with 3.5/5.5/6.5 secondaries; X8 uses K_REF=8 and clamp [0.67, 1.50], and the halves constant is 0.3818.
