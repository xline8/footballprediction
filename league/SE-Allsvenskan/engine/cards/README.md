# K-SE cards engine

Reads unified SE `yellow_home`, `yellow_away`, and direct `referee` from `data/se_matches.csv`. It uses 2021 warm-up, scores 2022–2024 at 3.5, and applies X8 referee shrinkage with an 8-match prior.

```text
python3 league/SE-Allsvenskan/engine/cards/run_k_se.py dev
python3 league/SE-Allsvenskan/engine/cards/run_k_se.py virgin --arms gate_zero x8
```

Outputs include dev/virgin JSON and CSV artifacts, fitted parameters, and conditional `predictions/k_se_virgin_predictions.csv`.
