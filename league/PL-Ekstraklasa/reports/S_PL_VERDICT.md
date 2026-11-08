# S-PL verdict — PASS (calibration PROVISIONAL) — GZ SHIPS

Preregistration: `prereg/PREREG_S_PL.md`; virgin is 2025/2026, n=306, read once. Calibration is actual − predicted.

## Dev primary-line table (LL@8.5)

| arm / baseline | 2022/23 | 2023/24 | 2024/25 | pooled |
|---|---:|---:|---:|---:|
| Gate Zero | 0.671103 | 0.679702 | 0.683213 | 0.678006 |
| RS | 0.670590 | 0.678099 | 0.683257 | 0.677315 |
| league base rate | 0.696888 | 0.692827 | 0.693385 | 0.694366 |
| naive trailing-10 | 0.679735 | 0.686878 | 0.693520 | 0.686711 |

Both pass dev. RS sign check versus Gate Zero is 2/3 (pass).

## Virgin table

| arm / baseline | LL@8.5 | actual over % | mean predicted % | calibration pp ± SE |
|---|---:|---:|---:|---:|
| Gate Zero | 0.673177 | 47.712 | 49.252 | −1.540 ± 2.805 |
| RS | 0.673989 | 47.712 | 49.340 | −1.628 ± 2.807 |
| league base rate | 0.692533 | 47.712 | 46.241 | +1.471 ± — |
| naive trailing-10 | 0.682006 | 47.712 | 46.068 | +1.644 ± — |

(Coordinator correction: the first draft of this table carried the
7.5-line rates in the actual/mean-predicted columns; the columns
above are the 8.5-line rates recomputed from the shipped CSV and
the data CSV. The calibration differences and LLs were unaffected.)

## Gate arithmetic

- Gate Zero: leg (i) **PASS** (0.673177 ≤ itself and ≤ best baseline 0.682006); leg (ii) **PROVISIONAL PASS** (|−1.540| pp breaches the 1.0 pp boundary by 0.540 pp, within 1 SE of 2.805 pp); leg (iii) exempt.
- RS: leg (i) **FAIL** (0.673989 > Gate Zero 0.673177), despite being below the best baseline; leg (ii) passes (1.628 pp ≤ 1.0 + 2.807 pp); leg (iii) is 2/3 and passes.

Only Gate Zero passes all required legs. Shipped arm: **GZ** (calibration provisional). Prediction CSV: `predictions/s_pl_virgin_predictions.csv` (306 rows). Fitted params: `engine/sot/fitted_params_virgin.json`. Verification: coordinator recomputed virgin LL@8.5 from the shipped predictions CSV = 0.673177 and calibration (actual − predicted) = −1.540 pp ± 2.805, matching results_virgin.json exactly.
