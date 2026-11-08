# G-ME goals engine

This goals-only Dixon-Coles engine reads `league/ME-1CFL/data/me_matches.csv`
and follows the frozen preregistration in `league/ME-1CFL/prereg/PREREG_G_ME.md`.
The development walk-forward fits one model per target season using matches
strictly before that season's first date, then scores 2022/2023, 2023/2024,
and 2024/2025 (539 matches total). The 2025/2026 and 2026/2027 rows are
excluded at load and are never read by this dev command.

The only arms are `gate_zero` and `shrink`. SHRINK multiplies each fitted
team attack/defence rating by `min(1, training_match_count / 6)` at prediction
time. Outputs are `results_dev.json` (tables, fit traces, gate and activity
checks) and `results_dev.csv` (one row per scored match).

Unseen teams use the league-mean prior represented by `a = d = 0.0`; SHRINK
also leaves these unseen-team ratings at zero. From this engine directory,
rerun with:

```text
python3 run_g_me.py dev
```

The runner writes `results_dev.json` and `results_dev.csv`, and prints the
independent 2024-equivalent climatology check, fitted home
advantage and rho for every target season, pooled metrics, arm activity, and
the mechanical dev-gate reading.

Virgin step (read once, 2025/2026, n=180): `python3 run_g_me.py virgin`
fits on all matches before 2025-08-04 (n=718), evaluates both arms, applies
the frozen gate legs mechanically, and writes `results_virgin.json`,
`fitted_params_virgin.json`, and
`league/ME-1CFL/predictions/g_me_virgin_predictions.csv` (shipped arm's
rows; Gate Zero's rows with `shipped_arm` empty when nothing ships).
`dc.py` also returns an `over05` probability (added for the 1H OU 0.5
presentation line); it changes no other probability — the dev run
reproduces byte-identically with it in place.
