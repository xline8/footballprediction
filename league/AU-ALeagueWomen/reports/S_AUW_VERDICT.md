# S-AUW verdict — PASS (PROVISIONAL, calibration leg) — RS ships

## Dev results — pooled and per-season LL@10.5

| Arm / baseline | 2022/2023 | 2023/2024 | 2024/2025 | pooled |
|---|---:|---:|---:|---:|
| Gate Zero | 0.671936 | 0.692562 | 0.687770 | 0.685236 |
| RS | 0.673430 | 0.689708 | 0.685955 | 0.683937 |
| League base rate | 0.693147 | 0.692089 | 0.699021 | 0.694965 |
| Naive trailing-10 | 0.665758 | 0.703752 | 0.697634 | 0.691271 |

Both arms beat both dev baselines; both pass the dev gate.

## Virgin results — 2025/2026, n=110

| Arm / baseline | LL@10.5 | mean P | actual rate | calibration breach | SE |
|---|---:|---:|---:|---:|---:|
| Gate Zero | 0.643941 | 0.37837 | 0.36364 | +1.473pp | 4.551pp |
| RS | 0.643041 | 0.37834 | 0.36364 | +1.471pp | 4.546pp |
| League base rate | 0.707349 | — | — | — | — |
| Naive trailing-10 | 0.668519 | — | — | — | — |

## Gate arithmetic

- Gate Zero: leg (i) `0.643941 <= 0.643941` and `0.643941 <= 0.668519` — PASS. Leg (ii) `1.473pp <= 1.000pp + 4.551pp` — PROVISIONAL PASS. Gate Zero is exempt from leg (iii).
- RS: leg (i) `0.643041 <= 0.643941` and `0.643041 <= 0.668519` — PASS. Leg (ii) `1.471pp <= 1.000pp + 4.546pp` — PROVISIONAL PASS. Dev sign check: 2/3 — PASS.

Both eligible; RS ships on lower virgin LL (`0.643041 < 0.643941`). Artifacts: `engine/sot/fitted_params_virgin.json` and `predictions/s_auw_virgin_predictions.csv`.
