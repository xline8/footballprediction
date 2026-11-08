# G-PE goals engine

Reads `../../data/pe_liga1_matches.csv` and keeps regular, non-awarded PE Liga 1 matches. DEV uses 2021 Fase 1/Fase 2 as seed and blocks through 2024 Clausura; virgin code is implemented for both 2025 blocks but was not run.

Run `python3 run_g_pe.py dev`. Outputs are `results_dev.json` and `results_dev.csv`. The PE port uses `home_absent_prev`/`away_absent_prev`, X2 offsets `a=-0.0645`, `d=0.1024`, and halves split `0.4377/0.5623` for later virgin presentation.
