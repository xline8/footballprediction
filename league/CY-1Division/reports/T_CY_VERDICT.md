# T-CY verdict — PROVISIONAL PASS — arm A ships

Prereg: `prereg/PREREG_T_CY.md`, frozen 2026-11-10. Primary line **18.5**;
virgin 2025/2026 n = **239**; calibration is actual minus predicted.

## Dev results — pooled LL@18.5

| Arm / baseline | LL |
|---|---:|
| A | 0.675723 |
| B | 0.675582 |
| C | 0.676355 |
| League base rate | 0.6951 |
| Naive trailing-10 | 0.6861 |

All three arms beat both baselines. Variant sign checks versus A: B 1/3,
C 1/3, so neither variant satisfies leg (iii).

## Virgin results — 2025/2026

| Arm / baseline | LL@18.5 | actual − mean P | SE |
|---|---:|---:|---:|
| A | 0.688140 | +1.468pp | 3.217pp |
| B | 0.689331 | +1.894pp | 3.219pp |
| C | 0.686630 | +1.530pp | 3.212pp |
| League base rate | 0.689767 | — | — |
| Naive trailing-10 | 0.717515 | — | — |

## Gate arithmetic

A passes leg (i): 0.688140 ≤ 0.688140 and ≤ best baseline 0.689767.
Its calibration breach beyond 1pp is 0.468pp, within 3.217pp SE, so leg
(ii) is PROVISIONAL. B has a higher virgin LL than A and fails leg (iii);
C has the lowest virgin LL but fails leg (iii) (1/3 sign). Therefore the
mechanical both-pass rule leaves A as the shipping arm.

**Ships:** A, with FT virgin predictions in
`predictions/t_cy_virgin_predictions.csv`.
