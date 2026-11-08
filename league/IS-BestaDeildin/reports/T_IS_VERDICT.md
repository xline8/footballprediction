# T-IS verdict — PASS (provisional, calibration leg) — arm B ships

Prereg: `prereg/PREREG_T_IS.md`. Dev pooled n=324; virgin 2026 n=162, read once for all three dev-passing arms. Primary line 27.5; ladder 26.5/27.5/28.5.

## Dev pooled LL@27.5

| Arm / baseline | LL |
|---|---:|
| A | 0.651941 |
| B | 0.651563 |
| C | 0.652358 |
| League base rate | 0.696203 |
| Naive trailing-10 | 0.656532 |

All arms beat both baselines. B sign check versus A is 1/2; C sign check is 0/2.

## Virgin 2026

| Arm / baseline | 26.5 | 27.5 | 28.5 | Calibration at 27.5 |
|---|---:|---:|---:|---:|
| A | 0.493027 | 0.559717 | 0.589422 | −7.135pp (SE 3.362pp) |
| B | 0.484408 | 0.553977 | 0.574416 | −3.446pp (SE 3.381pp) |
| C | 0.502783 | 0.566887 | 0.597149 | −8.671pp (SE 3.363pp) |
| League base rate | 0.536946 | 0.608400 | 0.653398 | — |
| Naive trailing-10 | 0.477730 | 0.556615 | 0.578721 | — |

Gate arithmetic: A fails leg (i), 0.559717 > best baseline 0.556615, and fails calibration beyond 1 SE. B passes leg (i), 0.553977 ≤ A and ≤ 0.556615, and calibration is provisional (3.446pp ≤ 1pp + 3.381pp); leg (iii) passes 1/2. C fails leg (i), calibration, and leg (iii). B is the sole eligible arm and ships.

**Ships:** arm B; fitted parameters and 2026 predictions are in `engine/total_shots/fitted_params_virgin.json` and `predictions/t_is_virgin_predictions.csv` (FT ladder plus frozen total-shots halves constant 0.4623).
