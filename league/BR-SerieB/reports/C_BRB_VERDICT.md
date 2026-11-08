# C-BRB verdict — PASS (calibration PROVISIONAL) — Gate Zero ships

Primary line 10.5; dev n=1,140 and virgin 2025 n=380. Calibration is ACTUAL − PREDICTED.

## Dev results

| Arm / baseline | LL@10.5 | Per-season sign vs GZ |
|---|---:|---:|
| Gate Zero | 0.69751 | 0.705195 / 0.690066 / 0.697257 |
| X7 | 0.69421 | 0.687441 / 0.706175 / 0.689002 (2/3) |
| League base rate | 0.70946 | — |
| Naive | 0.70964 | — |

Both arms pass the dev gate.

## Virgin results (2025)

| Arm / baseline | LL@10.5 | Calibration pp | SE pp |
|---|---:|---:|---:|
| Gate Zero | **0.686634** | −2.324 | 2.548 |
| X7 | 0.686634 | −2.324 | 2.548 |
| League base rate | 0.701658 | −8.486 | — |
| Naive | 0.703658 | −9.085 | — |

## Gate arithmetic

- Leg (i): both arms are ≤ Gate Zero and ≤ best baseline (0.701658). Pass.
- Leg (ii): both calibrations breach the 1.0pp clean boundary by 1.324pp, but lie within one SE of it: 2.324 ≤ 1+2.548. Provisional pass. (Coordinator correction: the harness originally stored the 9.5-line calibration, −1.196pp; the primary-line 10.5 value recomputed from the shipped predictions CSV is −2.324pp, SE 2.548. The verdict outcome is unchanged.)
- Leg (iii): X7 ≤ Gate Zero in 2/3 dev seasons. Pass.

Both-pass rule selects the simpler tied arm, Gate Zero. Fitted parameters are in `engine/corners/fitted_params_virgin.json`; predictions are in `predictions/c_brb_virgin_predictions.csv`.
