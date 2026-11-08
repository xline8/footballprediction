# C-BRB corners engine

Reads `league/BR-SerieB/data/brb_matches.csv`, uses the chronological corners mechanics, and scores the frozen 10.5 line. Arms are Gate Zero (X9) and X7. Dev uses 2021 seed and scores 2022–2024; virgin is 2025 only for dev-passing arms.

```text
python3 league/BR-SerieB/engine/corners/run_c_br.py dev
python3 league/BR-SerieB/engine/corners/run_c_br.py virgin --arms gate_zero x7
```

Outputs are written here. A shipped run writes `fitted_params_virgin.json` and `predictions/c_brb_virgin_predictions.csv`; the 1H/2H columns use the frozen corners split 0.472/0.528.
