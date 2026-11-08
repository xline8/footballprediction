# G-LT goals engine

This goals-only Dixon-Coles engine reads `league/LT-Toplyga/data/lt_matches.csv`.
The development walk-forward fits one model per target season using matches
strictly before that season's first date, then scores 2022, 2023, 2024, and
2025 (720 matches total). Season 2026 is filtered at load and is not part of
this command.

The only arms are `gate_zero` and `shrink`. SHRINK multiplies each fitted
team attack/defence rating by `min(1, training_match_count / 6)` at prediction
time. Outputs are `results_dev.json` (tables, fit traces, gate and activity
checks) and `results_dev.csv` (one row per scored match).

From the repository root, rerun with:

```text
python3 league/LT-Toplyga/engine/goals/run_g_lt.py dev
```

The runner prints the independent 2024 climatology check, fitted home
advantage and rho for every target season, pooled metrics, arm activity, and
the mechanical dev-gate reading. Virgin fitting and predictions are outside
this engine's scope.
