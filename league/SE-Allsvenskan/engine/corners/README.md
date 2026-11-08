# C-SE corners engine

Reads `data/se_matches.csv`, uses the chronological corners mechanics, SE primary line 10.5, and frozen 1H share 0.473. Dev uses 2021 seed and scores the next three seasons; virgin is 2025.

```text
python3 league/SE-Allsvenskan/engine/corners/run_c_se.py dev
python3 league/SE-Allsvenskan/engine/corners/run_c_se.py virgin --arms gate_zero x7
```

The engine writes dev/virgin results and conditional fitted parameters plus `predictions/c_se_virgin_predictions.csv`.
