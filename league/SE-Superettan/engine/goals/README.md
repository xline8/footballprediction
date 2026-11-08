# G-SE goals engine

Reads `data/se2_matches.csv`; empty xG uses the goals-only DC fallback. DEV warms 2021 and scores 2022–2025 with `gate_zero`, `shrink`, and `x2`.

```text
python3 league/SE-Superettan/engine/goals/run_g_se2.py dev
```

Outputs are `results_dev.json` and `results_dev.csv`.
