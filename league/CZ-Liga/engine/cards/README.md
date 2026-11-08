# K-CZ cards engine

Reads `league/CZ-Liga/data/cz_matches.csv` (phase != placement only).
Production model_cards pattern, Gate Zero ONLY (the X8 referee arm
is not registered for CZ-Liga: referee names are absent from every
dev-era payload — FEATURES X8). Target = event-unified yellows
(`yellow_home + yellow_away` from matchFacts card events). Primary
line 3.5, ladder 2.5/3.5/4.5. Dev: warm-up 2021/2022, scored
2022/2023–2024/2025 (n = 810); virgin 2025/2026 read once only if
the dev gate passes.

```text
python3 league/CZ-Liga/engine/cards/run_k_cz.py dev
python3 league/CZ-Liga/engine/cards/run_k_cz.py virgin --arms gate_zero
```

Outputs `results_dev.json`, conditional `results_virgin.json`,
`fitted_params_virgin.json`, and on PASS
`predictions/k_cz_virgin_predictions.csv` (1H/2H via frozen 0.3150).
