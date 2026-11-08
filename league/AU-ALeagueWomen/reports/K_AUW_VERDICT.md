# K-AUW verdict — PASS (PROVISIONAL, calibration leg) — X8 ships

## Dev results — LL@2.5

| Arm / baseline | 2022/2023 | 2023/2024 | 2024/2025 | pooled |
|---|---:|---:|---:|---:|
| Gate Zero | 0.708391 | 0.671335 | 0.657860 | 0.676237 |
| X8 | 0.707941 | 0.664724 | 0.656808 | 0.673358 |
| League base rate | 0.702815 | 0.684967 | 0.662501 | 0.681353 |
| Naive trailing-10 | 0.728414 | 0.673745 | 0.646358 | 0.678170 |

Both arms beat both dev baselines; both pass the dev gate.

## Virgin results — 2025/2026, n=110

| Arm / baseline | LL@2.5 | mean P | actual rate | calibration breach | SE |
|---|---:|---:|---:|---:|---:|
| Gate Zero | 0.604703 | 0.34556 | 0.32727 | +1.828pp | 4.363pp |
| X8 | 0.597092 | 0.34343 | 0.32727 | +1.616pp | 4.328pp |
| League base rate | 0.646756 | — | — | — | — |
| Naive trailing-10 | 0.627263 | — | — | — | — |

## Gate arithmetic

- Gate Zero: leg (i) `0.604703 <= 0.604703` and `0.604703 <= 0.627263` — PASS. Leg (ii) `1.828pp <= 1.000pp + 4.363pp` — PROVISIONAL PASS. Gate Zero is exempt from leg (iii).
- X8: leg (i) `0.597092 <= 0.604703` and `0.597092 <= 0.627263` — PASS. Leg (ii) `1.616pp <= 1.000pp + 4.328pp` — PROVISIONAL PASS. Dev sign check: 3/3 — PASS.

Both eligible; X8 ships on lower virgin LL (`0.597092 < 0.604703`). Artifacts: `engine/cards/fitted_params_virgin.json` and `predictions/k_auw_virgin_predictions.csv`.
