# S-SK shots-on-target engine

Reads `league/SK-1Liga/data/sk_matches.csv` (phase != playoff only).
Production model_sot v5 pattern (joint Poisson ridge + NB +
Beta-Binomial on-target ratio, constants per PREREG_S_SK). Arms:
`GZ` (Gate Zero), `RS` (BB prior 200 → 20,000). Primary line 8.5,
ladder 7.5/8.5/9.5. Per-match walk-forward, date-grouped,
predict-then-update; 2021/2022 warm-up unscored; dev scored
2022/2023–2024/2025 (stats-target n = 568); virgin 2025/2026 read
once only for dev-passing arms. FT-only market (no halves).
Declared risk: the raw total_shots input changes counting at
2025/2026 (see prereg) — the gate judges the virgin result as-is.

```text
python3 league/SK-1Liga/engine/sot/run_s_sk.py dev
python3 league/SK-1Liga/engine/sot/run_s_sk.py virgin-predict --arm GZ
```

Outputs `results_dev.json/.csv`, conditional `results_virgin.json`,
`fitted_params_virgin.json`, and on PASS
`predictions/s_sk_virgin_predictions.csv`.
