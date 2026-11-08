# G-DK2 goals engine

Gate Zero is the production Dixon-Coles goals-only pattern: expanding,
season-blocked fits, half-life 270 and the production rho grid. Arms are
gate_zero; shrink (teams with fewer than six prior in-league matches scaled
by n/6); and x2 (parent DK-1Division mover transplant defined in
run_g_dk2.py). The DK-2 feed has no xG fields, so the DK-1 x3 arm is dropped.

Run `python3 run_g_dk2.py dev` for the DEV phase. Outputs are
`results_dev.json` and `dev_predictions.csv`. The virgin phase is
`python3 run_g_dk2.py virgin`, but is deliberately not run in Phase B.
