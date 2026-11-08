# K-DK cards engine

Reads unified DK `yellow_home`, `yellow_away`, and direct `referee` from `data/dk_matches.csv`. It uses 2021/2022 warm-up, scores 2022/2023–2024/2025 at 3.5, and applies X8 referee shrinkage with an 8-match prior.

```text
python3 league/DK-Superligaen/engine/cards/run_k_dk.py dev
python3 league/DK-Superligaen/engine/cards/run_k_dk.py virgin --arms gate_zero x8
```

Outputs include dev/virgin JSON and CSV artifacts, fitted parameters, and conditional `predictions/k_dk_virgin_predictions.csv`.
