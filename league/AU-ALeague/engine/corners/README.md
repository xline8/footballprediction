# C-AU corners engine

Reads `data/au_matches.csv`, uses the chronological corners mechanics, AU gate line 10.5 with ladder 9.5/10.5/11.5, and frozen 1H share 0.452. Dev uses 2021/2022 seed and scores the next three seasons; virgin is 2025/2026.

```text
python3 league/AU-ALeague/engine/corners/run_c_au.py dev
python3 league/AU-ALeague/engine/corners/run_c_au.py virgin --arms gate_zero x7
```

The engine writes dev/virgin results and conditional fitted parameters plus `predictions/c_au_virgin_predictions.csv`.
