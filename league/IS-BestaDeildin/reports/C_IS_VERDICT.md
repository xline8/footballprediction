# C-IS verdict — PASS (provisional, calibration leg) — X7 ships

Prereg: `prereg/PREREG_C_IS.md`. Dev pooled n=324; virgin 2026 n=162, read once for both dev-passing arms. Primary line 11.5; ladder 10.5/11.5/12.5.

## Dev pooled LL@11.5

| Arm / baseline | LL |
|---|---:|
| Gate Zero | 0.696203 |
| X7 | 0.692811 |
| League base rate | 0.741918 |
| Naive trailing-10 | 0.731999 |

Both arms beat both baselines. X7 dev sign check versus Gate Zero is 1/2, so pass.

## Virgin 2026

| Arm / baseline | 10.5 | 11.5 | 12.5 | Calibration at 11.5 |
|---|---:|---:|---:|---:|
| Gate Zero | 0.637021 | 0.698517 | 0.716690 | −2.598pp (SE 3.952pp) |
| X7 | 0.606973 | 0.674422 | 0.687933 | −2.353pp (SE 3.863pp) |
| League base rate | 0.621187 | 0.689293 | 0.697701 | — |
| Naive trailing-10 | 0.776263 | 0.762011 | 0.712584 | — |

Gate arithmetic: GZ fails leg (i), 0.698517 > best baseline 0.689293; calibration is provisional (2.598pp ≤ 1pp + 3.952pp). X7 passes leg (i), 0.674422 ≤ GZ and ≤ 0.689293; calibration is provisional (2.353pp ≤ 1pp + 3.863pp); leg (iii) passes 1/2. X7 is the sole eligible arm and ships.

**Ships:** X7; fitted parameters and 2026 predictions are in `engine/corners/fitted_params_virgin.json` and `predictions/c_is_virgin_predictions.csv` (FT ladder plus frozen corners halves constant 0.4707).
