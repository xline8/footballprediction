# T-PE total-shots engine

Loads regular, non-awarded PE rows and targets unified shots: rich `shotsontarget + shotsofftarget`, sparse `total_shots`. DEV uses the frozen 2021 seed and six blocks through 2024 Clausura; virgin code targets both 2025 blocks but was not run.

Run `python3 run_t_pe.py dev`. Outputs are `results_dev.json`, `results_dev.csv`, and fitted DEV parameters. Primary line is 19.5, with 17.5/18.5/20.5/21.5 secondaries; `M_BAR=19.727`, arms are A/B/C, and the halves constant is 0.4662.
