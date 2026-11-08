# K-PL verdict

Preregistration: `prereg/PREREG_K_PL.md`; virgin is 2025/2026, n=306, read once. Calibration is actual − predicted.

## Dev primary-line table (LL@3.5)

| arm / baseline | pooled LL |
|---|---:|
| Gate Zero | 0.683601 |
| X8 | 0.678552 |
| league base rate | 0.688893 |
| naive trailing-10 | 0.700911 |

Both arms pass dev. X8’s per-season sign check versus Gate Zero is 2/3 (pass).

## Virgin table

| arm / baseline | LL@3.5 | actual over % | mean predicted % | calibration pp ± SE |
|---|---:|---:|---:|---:|
| Gate Zero | 0.696756 | 55.556 | 54.526 | +1.029 ± 2.871 |
| X8 | 0.677894 | 55.556 | 54.832 | +0.724 ± 2.818 |
| league base rate | 0.687789 | 55.556 | 54.602 | +0.954 ± — |
| naive trailing-10 | 0.705195 | 55.556 | 53.845 | +1.711 ± — |

X8 virgin fallback counts: 41 unknown referee identities and 15 thin-history appointments; known referee coverage was 265/306 = 86.6%.

## Gate arithmetic

- Gate Zero: leg (i) **FAIL** (0.696756 > best baseline 0.687789); leg (ii) passes (+1.029 pp ≤ 1.0 + 2.871 pp); leg (iii) exempt.
- X8: leg (i) **PASS** (0.677894 ≤ Gate Zero 0.696756 and ≤ 0.687789); leg (ii) **PASS** (+0.724 pp ≤ 1.0 + 2.818 pp); leg (iii) **PASS**, 2/3.

Shipped arm: **X8** (clean PASS — calibration +0.724 pp is inside the 1.0 pp boundary). Prediction CSV: `predictions/k_pl_virgin_predictions.csv` (306 rows). Fitted params: `engine/cards/fitted_params_virgin.json`. Verification: coordinator recomputed virgin LL@3.5 from the shipped predictions CSV against the data CSV's unified yellows = 0.677894 and calibration = +0.724 pp ± 2.818, matching results_virgin.json exactly; fallback count 56 (41 unknown referee + 15 thin-history) confirmed in the CSV.
