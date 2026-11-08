# C-AUW verdict — PASS (PROVISIONAL, calibration leg) — X7 ships

## Dev results — LL@9.5

| Arm / baseline | 2022/2023 | 2023/2024 | 2024/2025 | pooled |
|---|---:|---:|---:|---:|
| Gate Zero | 0.736875 | 0.679680 | 0.693509 | 0.700197 |
| X7 | 0.708822 | 0.690937 | 0.690554 | 0.695593 |
| League base rate | 0.729467 | 0.698282 | 0.717365 | 0.713786 |
| Naive trailing-10 | 0.734527 | 0.709827 | 0.710280 | 0.716623 |

Both arms beat both dev baselines; both pass the dev gate.

## Virgin results — 2025/2026, n=110

| Arm / baseline | LL@9.5 | mean P | actual rate | calibration breach | SE |
|---|---:|---:|---:|---:|---:|
| Gate Zero | 0.694234 | 0.40361 | 0.43636 | -3.275pp | 4.783pp |
| X7 | 0.684884 | 0.40432 | 0.43636 | -3.205pp | 4.739pp |
| League base rate | 0.701514 | — | — | — | — |
| Naive trailing-10 | 0.688210 | — | — | — | — |

## Gate arithmetic

- Gate Zero: leg (i) `0.694234 <= 0.694234` and `0.694234 <= 0.688210` — FAIL. Leg (ii) `3.275pp <= 1.000pp + 4.783pp` — PROVISIONAL PASS. Gate Zero is exempt from leg (iii).
- X7: leg (i) `0.684884 <= 0.694234` and `0.684884 <= 0.688210` — PASS. Leg (ii) `3.205pp <= 1.000pp + 4.739pp` — PROVISIONAL PASS. Dev sign check: 2/3 — PASS.

X7 is the only eligible arm and ships. Artifacts: `engine/corners/fitted_params_virgin.json` and `predictions/c_auw_virgin_predictions.csv`.
