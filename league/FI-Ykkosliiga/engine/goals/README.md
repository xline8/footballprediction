# G-YK goals engine

Reads `league/FI-Ykkosliiga/data/yk_matches.csv`; its xG/stat columns are empty, so the goals-only DC fallback is used. DEV warms 2021 and scores 2022–2025 with Gate Zero, SHRINK, and the pooled in-corpus entrant X2 arm.

```text
<repo>/.venv/bin/python league/FI-Ykkosliiga/engine/goals/run_g_yk.py dev
```

DEV outputs are `results_dev.json` and `results_dev.csv`. Coordinator-gated virgin outputs, when authorized, are `results_virgin.json`, `fitted_params_virgin.json`, and `predictions/g_yk_virgin_predictions.csv`. The dev gate is checked independently for each arm: pooled 1X2 LL and RPS must beat the per-season expanding climatology, and pooled OU2.5 LL must beat its `oull_2_5` base-rate baseline. `virgin-metrics` reads 2026 only for the arms that pass; `virgin-predict --arm X` refuses an arm that fails this gate. These virgin commands are coordinator-gated and must not be run by the DEV workflow.

The X2 entrant offset pools completed entrant transitions in the Ykkösliiga corpus, requires at least three transitions, clamps multipliers to [0.8, 1.25], and applies in an entrant's first Ykkösliiga season only.
