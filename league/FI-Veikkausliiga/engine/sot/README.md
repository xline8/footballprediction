# S-FI shots-on-target engine

Reads `data/fi_matches.csv` and warms 2021 (130 stats rows), scoring 2022–2025 at the FT ladder 7.5/8.5/9.5; primary line is 8.5. Arms are Gate Zero and RS.

```text
~/workspace/footballprediction/.venv/bin/python league/FI-Veikkausliiga/engine/sot/run_s_fi.py dev
```

Outputs are `results_dev.json` and `results_dev.csv`.
