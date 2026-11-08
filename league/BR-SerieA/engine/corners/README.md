# C-BR corners engine

Reads `league/BR-SerieA/data/br_matches.csv`, uses the chronological corners mechanics, BR line 10.5, and frozen 1H share 0.474. Dev uses 2021 seed and scores 2022–2024; virgin is 2025.

```text
python3 league/BR-SerieA/engine/corners/run_c_br.py dev
python3 league/BR-SerieA/engine/corners/run_c_br.py virgin --arms gate_zero x7
```

The engine writes dev/virgin results and conditional fitted parameters plus `predictions/c_br_virgin_predictions.csv`.
