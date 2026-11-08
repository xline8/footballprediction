# K-BE cards engine

Reads unified BE `yellow_home`, `yellow_away`, and direct `referee` from `data/be_matches.csv`. It uses 2021/2022 warm-up, scores n=956 in 2022/2023–2024/2025 at primary line 3.5, and applies X8 referee shrinkage with an 8-match prior. Virgin n=313; frozen halves shares are 0.317/0.683.

```text
python3 league/BE-FirstDivisionA/engine/cards/run_k_be.py dev
python3 league/BE-FirstDivisionA/engine/cards/run_k_be.py virgin --arms gate_zero x8
```

Outputs include dev/virgin JSON and CSV artifacts, fitted parameters, and conditional `predictions/k_be_virgin_predictions.csv`.
