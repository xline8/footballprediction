# K-AU cards engine

Reads AU `yellow_home`, `yellow_away` from `data/au_matches.csv`. It uses 2021/2022 warm-up and scores 2022/2023–2024/2025 at 3.5. This engine is Gate-Zero-only: the preregistered X8 referee arm is not built because AU referee coverage and the strictness trait failed the adoption criteria; no referee covariate is used.

```text
python3 league/AU-ALeague/engine/cards/run_k_au.py dev
python3 league/AU-ALeague/engine/cards/run_k_au.py virgin --arms gate_zero
```

Outputs include dev/virgin JSON and CSV artifacts, fitted parameters, and conditional `predictions/k_au_virgin_predictions.csv`.
