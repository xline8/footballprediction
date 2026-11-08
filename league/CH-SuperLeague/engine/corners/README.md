# C-CH corners engine

Reads `data/ch_matches.csv`, uses the chronological corners mechanics, CH line 9.5, and frozen 1H share 0.488. Dev uses 2021/2022 seed and scores the next three seasons; virgin is 2025/2026.

```text
python3 league/CH-SuperLeague/engine/corners/run_c_dk.py dev
python3 league/CH-SuperLeague/engine/corners/run_c_dk.py virgin --arms gate_zero x7
```

The engine writes dev/virgin results and conditional fitted parameters plus `predictions/c_ch_virgin_predictions.csv`.
