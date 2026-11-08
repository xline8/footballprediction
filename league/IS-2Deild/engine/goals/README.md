# G-IS2 goals engine

Run the dev walk-forward with `python3 run_g_is2.py dev` from this directory. It reads only the allowed 2021–2025 rows from `../../data/is2_matches.csv`, trains once per target season, and writes `results_dev.json` plus one per-match row per dev fixture to `results_dev.csv`.

The outputs contain Gate Zero, SHRINK, X2, and expanding pre-target climatology metrics. Gate Zero uses the fitted Dixon–Coles ratings; SHRINK scales each fitted attack and defence log-rating by the target-season matches played before kickoff; X2 adds gated, source-specific entrant shifts in log space after SHRINK.
