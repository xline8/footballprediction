# G-PA-LPF goals engine

This engine reads `league/PA-LPF/data/pa_lpf_matches.csv`, excludes awarded
and playoff matches, and uses only seasons 2023–2025 in DEV. The scored folds
are 2024 and 2025 (191 matches each); 2023 is the 120-match seed. DEV asserts
`scored_n == 382` and never loads the virgin season.

Run DEV from the worktree root:

```bash
python3 league/PA-LPF/engine/goals/run_g_pa_lpf.py --dev
```

This writes `results_dev.json` and `results_dev.csv`, with two rows per
scored match. The CSV contains Gate Zero and SHRINK predictions plus the
climatology and trailing-10 naive baseline columns. The DC fit uses the
production 14-sweep, damping 0.7, smoothing 0.25, MAXG 10, rho grid, and
270-day half-life. SHRINK multiplies each team's attack and defence
components by `n/6` at prediction time when `n < 6` prior training matches.

The frozen EDA audit predicts only n=0 newcomers in the two DEV folds, so
SHRINK should be identical to Gate Zero; the DEV JSON records the audit and
the output comparison should confirm it.

After the coordinator verifies DEV, the preregistered virgin command is:

```bash
python3 league/PA-LPF/engine/goals/run_g_pa_lpf.py --virgin
```

It first checks the frozen DEV gate. If Gate Zero failed, it writes only the
not-read marker and creates no predictions or fitted-parameters file. If the
gate passed, the coordinator may run it once to fit 2023–2025 and predict the
2026 virgin window, writing `results_virgin.json`,
`fitted_params_virgin.json`, and
`league/PA-LPF/predictions/g_pa_lpf_virgin_predictions.csv`.
