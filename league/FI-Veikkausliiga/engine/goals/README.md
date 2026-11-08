# G-FI goals engine

Reads `data/fi_matches.csv`; the feed has no xG, so the goals-only DC fallback is used. DEV warms 2021 and scores 2022–2025 with Gate Zero, SHRINK, and the in-corpus entrant X2 arm.

```text
~/workspace/footballprediction/.venv/bin/python league/FI-Veikkausliiga/engine/goals/run_g_fi.py dev
```

Outputs are `results_dev.json` and `results_dev.csv`.
