# K-FI cards engine

Reads event-derived unified yellows from `data/fi_matches.csv`, warms 2021, and scores 2022–2025 at the FT ladder 3.5/4.5; primary line is 3.5. Gate Zero only, with referee fallback machinery retained.

```text
~/workspace/footballprediction/.venv/bin/python league/FI-Veikkausliiga/engine/cards/run_k_fi.py dev
```

Outputs are `results_dev.json` and `results_dev.csv`.
