# C-SK corners engine

Reads `league/SK-1Liga/data/sk_matches.csv` (phase != playoff only).
Production corners_v3 pattern, Gate Zero only, covariate =
BallPossesion alone (big_chance / touches_opp_box have no dev-era
data in this league — PREREG_C_SK). Primary line 9.5, ladder
8.5/9.5/10.5. Dev: seed 2021/2022, scored 2022/2023–2024/2025
(stats-target n = 568); virgin 2025/2026 read once only if the dev
gate passes. Predictions are FT-only (`halves_share_1h = null` —
no dev-era period splits exist in this league).

```text
python3 league/SK-1Liga/engine/corners/run_c_sk.py dev
python3 league/SK-1Liga/engine/corners/run_c_sk.py virgin --arms gate_zero
```

Outputs `results_dev.json/.csv`, conditional `results_virgin.json`,
`fitted_params_virgin.json`, and on PASS
`predictions/c_sk_virgin_predictions.csv`.
