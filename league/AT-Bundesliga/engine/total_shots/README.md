# T-AT total-shots engine

This engine implements the AT-Bundesliga total-shots preregistration in
[`league/AT-Bundesliga/prereg/PREREG_T_AT.md`](../../prereg/PREREG_T_AT.md).
It reads `league/AT-Bundesliga/data/at_matches.csv`, whose season labels
are `YYYY/YYYY` strings, and uses total shots from the full-match home and
away shot columns. The development loader reads only 2021/2022 through
2024/2025, with 2021/2022 as warm-up and 2022/2023 as tuning. It never
loads 2025/2026 or 2026/2027 during development.

Run the development pass with the repository virtualenv when available:

```text
~/workspace/footballprediction/.venv/bin/python league/AT-Bundesliga/engine/total_shots/run_t_j1.py dev
```

Otherwise use `python3` from the repository root. The dev pass writes
`results_dev.json`, `results_dev.csv`, and `fitted_params.json` here. Only
arms A (the v1 pattern) and C (the trailing-r variant) are run. The
`gate_pool` rows are pooled over exactly 2023/2024 and 2024/2025, n=390,
and are reported alongside the per-season rows for both arms and both
baselines.

The virgin step is deliberately not part of the development rerun. After
reviewing the recorded gate, it may be invoked explicitly; it carries state
through 2024/2025 and scores 2025/2026 only:

```text
~/workspace/footballprediction/.venv/bin/python league/AT-Bundesliga/engine/total_shots/run_t_j1.py virgin --export-arm A
```

Virgin output is `results_virgin.json`; an exported arm writes
`league/AT-Bundesliga/predictions/t_at_virgin_predictions.csv`. The
prediction file contains the full-time ladder, the arm's NB `r`, and
presentation-only first-/second-half ladders made from the frozen 0.454 /
0.546 split. The preregistration is the governing document.
