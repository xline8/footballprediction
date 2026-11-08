# C-CY verdict — PASS — Gate Zero ships

Prereg: `prereg/PREREG_C_CY.md`, frozen 2026-11-10. Primary line **9.5**;
virgin 2025/2026 n = **239**; calibration is actual minus predicted.

## Dev results — pooled LL@9.5

| Arm / baseline | LL |
|---|---:|
| Gate Zero | 0.685501 |
| League base rate | 0.711811 |
| Naive trailing-10 | 0.711474 |

Gate Zero beats both baselines and passes the dev gate.

## Virgin results — 2025/2026

| Arm / baseline | LL@9.5 | actual − mean P | SE |
|---|---:|---:|---:|
| Gate Zero | 0.688133 | −0.261pp | 3.224pp |
| League base rate | 0.690459 | — | — |
| Naive trailing-10 | 0.700242 | — | — |

## Gate arithmetic

Leg (i): 0.688133 ≤ Gate Zero and ≤ best baseline 0.690459. Leg (ii):
|−0.261pp| ≤ 1.0pp, a clean pass. There is no variant leg to apply.

**Ships:** Gate Zero, with FT virgin predictions in
`predictions/c_cy_virgin_predictions.csv`.
