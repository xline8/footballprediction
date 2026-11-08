# G-COA goals engine

This engine fits the preregistered goals-only Dixon-Coles model for CO-PrimeraA. It loads `data/co_primeraa_matches.csv`, uses FotMob team IDs, tournament-blocked expanding fits, 270-day half-life, 14 sweeps, damping 0.7, smoothing 0.25, MAXG 10, and the frozen rho grid. The arms are `gate_zero` and `x2`; X2 replaces a flagged mover-up team's fitted attack with `ln(0.81)` and defence with `ln(1.18)` at prediction time.

Run from this directory with `~/workspace/footballprediction/.venv/bin/python run_g_coa.py dev`, then `~/workspace/footballprediction/.venv/bin/python run_g_coa.py virgin`. Dev writes `results_dev.json` and `results_dev.csv`. A passing virgin gate writes `results_virgin.json`, `fitted_params_virgin.json`, and `../../predictions/g_coa_virgin_predictions.csv`.

The dev gate is pooled 1X2 log loss, RPS, and OU2.5 log loss versus climatology. The trailing-10 naive baseline is reporting-only. Virgin selection applies the frozen LL, calibration, and X2 per-season sign legs; virgin rows never include `2026 - Clausura`, and half means use 0.4706 / 0.5294.
