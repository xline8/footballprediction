# G-IEFD goals engine

This engine fits the preregistered Dixon–Coles goals model for Ireland First
Division regular-season matches.

## Inputs

- `league/IE-FirstDivision/data/ie_first_division_matches.csv`
- Regular rows only (`phase == "regular"`), seasons 2021–2026.
- Goals are the sole observation input; xGH/xGA are always `None`.

## Arms

- `gate_zero`: the unmodified goals-only reference model.
- `x2`: Gate Zero plus the preregistered relegated-mover prior.

Mover names are frozen per season from the EDA mover check and resolved to
CSV team IDs at runtime by `arms.mover_ids`.

## Rerun

From the worktree root:

```text
python3 league/IE-FirstDivision/engine/goals/run_g_iefd.py dev
python3 league/IE-FirstDivision/engine/goals/run_g_iefd.py virgin-metrics
python3 league/IE-FirstDivision/engine/goals/run_g_iefd.py virgin-predict --arm gate_zero
```

The dev run evaluates 2022–2025 using 2021 as seed. Virgin commands read and
predict the 2026 regular season only after the dev gate permits it.

## Outputs

Dev results are written to this directory as `results_dev.json` and
`results_dev.csv`. Virgin fitting writes `results_virgin.json` and
`fitted_params_virgin.json`; prediction output is
`league/IE-FirstDivision/predictions/g_iefd_virgin_predictions.csv`.
Virgin half-time presentation uses the frozen 0.441 split: 0.441 of FT
lambdas for 1H and 0.559 for 2H.
