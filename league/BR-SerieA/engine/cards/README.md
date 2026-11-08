# K-BR cards engine

Reads unified `yellow_unified_home`, `yellow_unified_away`, and direct `referee` from `league/BR-SerieA/data/br_matches.csv`. It uses 2021 warm-up, scores 2022–2024 at 4.5, and applies X8 referee shrinkage with an 8-match prior.

```text
python3 league/BR-SerieA/engine/cards/run_k_br.py dev
python3 league/BR-SerieA/engine/cards/run_k_br.py virgin --arms gate_zero x8
```

Outputs include dev/virgin JSON and CSV artifacts, fitted parameters, and conditional `predictions/k_br_virgin_predictions.csv`.
