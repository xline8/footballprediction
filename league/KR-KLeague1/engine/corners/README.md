# C-KR corners engine

Reads `data/kr_matches.csv`, uses the chronological corners mechanics, KR primary line 8.5, and frozen 1H share 0.429. Dev uses 2021 seed and scores the next three seasons; virgin is 2025.

```text
python3 league/KR-KLeague1/engine/corners/run_c_kr.py dev
python3 league/KR-KLeague1/engine/corners/run_c_kr.py virgin --arms gate_zero x7
```

The engine writes dev/virgin results and conditional fitted parameters plus `predictions/c_kr_virgin_predictions.csv`.
