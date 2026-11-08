# G-BEB goals engine

This engine fits goals-only Dixon–Coles models on `data/beb_matches.csv`,
keying teams by FotMob ID. It has three arms: `gate_zero`, `shrink`, and
`x2` (the SHRINK arm plus the frozen BE-A relegated-mover prior). All phases
are ordinary rows; no phase feature is used. The frozen presentation-only
halves constant is `0.434014`.

DEV uses the 2021/2022 seed and evaluates 2022/2023, 2023/2024, and
2024/2025. It writes `results_dev.json` and `predictions_dev.csv` in this
directory. Run:

```text
python3 league/BE-FirstDivisionB/engine/goals/run_g_beb.py dev
```

The `virgin` command exists as a coordinator boundary but is disabled here.
Virgin mode is coordinator-run only and must not be run during this phase.
