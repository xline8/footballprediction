# K-DE2 cards engine

Reads unified `yellow_home`, `yellow_away`, and direct `referee` from `data/de2_matches.csv`. It uses 2021/2022 warm-up, scores n=918 at primary line 4.5, and applies X8 referee shrinkage with an 8-match prior. Virgin n=306; frozen halves shares are 0.346/0.654.

```text
python3 league/DE-2Bundesliga/engine/cards/run_k_de2.py dev
python3 league/DE-2Bundesliga/engine/cards/run_k_de2.py virgin --arms gate_zero x8
```

Outputs include dev/virgin JSON and CSV artifacts, fitted parameters, and conditional `predictions/k_de2_virgin_predictions.csv`.
