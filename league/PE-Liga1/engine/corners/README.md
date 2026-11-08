# C-PE corners engine

Loads regular, non-awarded rows from `../../data/pe_liga1_matches.csv`; rolling shot factors use unified PE shots. DEV uses the frozen 2021 seed and six blocks through 2024 Clausura. Virgin code targets both 2025 blocks but was not run.

Run `python3 run_c_pe.py dev`. Outputs are `results_dev.json` and `results_dev.csv`. Primary line is 9.5, with 8.5/10.5/11.5 secondaries; arms are Gate Zero and X7, and the halves constant is 0.4817.
