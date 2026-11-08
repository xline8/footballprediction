# C-BE corners engine

Reads `data/be_matches.csv`, uses the chronological corners mechanics, primary line 9.5, and frozen halves shares 0.471/0.529. Dev uses 2021/2022 seed and scores n=956 across the next three seasons; virgin is 2025/2026 (n=313).

```text
python3 league/BE-FirstDivisionA/engine/corners/run_c_be.py dev
python3 league/BE-FirstDivisionA/engine/corners/run_c_be.py virgin --arms gate_zero x7
```

The engine writes dev/virgin results and conditional fitted parameters plus `predictions/c_be_virgin_predictions.csv`.
