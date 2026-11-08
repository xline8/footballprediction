# G-FEDA DEV engine

This directory contains the Phase B development-only goals engine. It reads
`data/feda_matches.csv`, admits only blocks 2021–2025, fits one goals-only
Dixon–Coles model before each scored block, and predicts the complete block.
The arms are `gate_zero` and `x2`; X2 applies the frozen newcomer offsets
from `prereg/PREREG_G_FEDA.md`. The trailing-10 baseline uses each team's last
ten pre-cutoff goal-for and goal-against means, with the league mean fallback.

Run from this directory with:

    /home/hatch/workspace/footballprediction/.venv/bin/python run_g_feda.py --dev

Outputs are `results_dev.json` and `results_dev.csv`. No virgin outputs or
predictions are produced by this runner.
