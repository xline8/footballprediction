# S-BRB verdict — PASS (calibration PROVISIONAL) — arm RS ships

Primary line 7.5; dev n=1,140 and virgin 2025 n=380. Calibration is ACTUAL − PREDICTED.

## Dev results

| Arm / baseline | LL@7.5 | Per-season 2022 / 2023 / 2024 |
|---|---:|---|
| Gate Zero | 0.69241 | 0.691851 / 0.699648 / 0.685731 |
| RS | 0.69105 | 0.691213 / 0.697026 / 0.684917 |
| League base rate | 0.73521 | — |
| Naive | 0.70246 | — |

Both arms pass the recorded dev gate; RS is no worse than Gate Zero in 3/3 dev seasons.

## Virgin results (2025)

| Arm / baseline | LL@7.5 | Calibration pp | SE pp |
|---|---:|---:|---:|
| Gate Zero | 0.673342 | +1.111 | 2.518 |
| RS | **0.671390** | +1.088 | 2.513 |
| League base rate | 0.682997 | +6.250 | — |
| Naive | 0.676768 | +0.448 | — |

## Gate arithmetic

- Leg (i): GZ 0.673342 ≤ best baseline 0.676768; RS 0.671390 ≤ GZ and ≤ best baseline. Both pass.
- Leg (ii): GZ 1.111pp and RS 1.088pp exceed the clean 1.0pp boundary, but each is within one SE of it (provisional pass: 1.111 ≤ 1+2.518; 1.088 ≤ 1+2.513).
- Leg (iii): RS ≤ GZ in 3/3 dev seasons. Pass.

Both arms pass; lower virgin LL ships RS. Virgin fitted parameters are in `engine/sot/fitted_params_virgin.json`, and predictions are in `predictions/s_brb_virgin_predictions.csv`.
