# K-KR cards engine

Reads unified KR `yellow_home`, `yellow_away`, and direct `referee` from `data/kr_matches.csv`. It uses 2021 warm-up, scores 2022–2024 at 3.5, and applies X8 referee shrinkage with an 8-match prior.

```text
python3 league/KR-KLeague1/engine/cards/run_k_kr.py dev
python3 league/KR-KLeague1/engine/cards/run_k_kr.py virgin --arms gate_zero x8
```

Outputs include dev/virgin JSON and CSV artifacts, fitted parameters, and conditional `predictions/k_kr_virgin_predictions.csv`.
