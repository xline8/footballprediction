# S-PE shots-on-target engine

Loads regular, non-awarded rows from `../../data/pe_liga1_matches.csv`; total-shots inputs use rich `shotsontarget + shotsofftarget` and sparse `total_shots`. DEV uses the frozen 2021 seed and six blocks through 2024 Clausura. Virgin code targets both 2025 blocks but was not run.

Run `python3 run_s_pe.py dev`. Outputs are `results_dev.json` and `results_dev.csv`. Primary line is 8.5, with 6.5/7.5/9.5/10.5 secondaries; arms are GZ (ratio prior 200) and RS (20,000), and the halves constant is 0.4611.
