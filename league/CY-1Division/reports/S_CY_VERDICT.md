# S-CY verdict — FAIL — nothing ships

Prereg: `prereg/PREREG_S_CY.md`, frozen 2026-11-10. Primary line **8.5**;
virgin 2025/2026 n = **239**; calibration is actual minus predicted.

## Dev results — pooled LL@8.5

| Arm / baseline | LL |
|---|---:|
| Gate Zero | 0.6842 |
| RS | 0.6841 |
| League base rate | 0.7013 |
| Naive trailing-10 | 0.6961 |

Both arms beat both baselines; both survive dev. Sign check for RS is 2/3.

## Virgin results — 2025/2026

| Arm / baseline | LL@8.5 | actual − mean P | SE |
|---|---:|---:|---:|
| Gate Zero | 0.697409 | −3.405pp | 3.247pp |
| RS | 0.697314 | −3.338pp | 3.247pp |
| League base rate | 0.697198 | — | — |
| Naive trailing-10 | 0.708688 | — | — |

## Gate arithmetic

Leg (i) fails for both arms: Gate Zero 0.697409 > best baseline 0.697198;
RS 0.697314 > 0.697198. Leg (ii) is PROVISIONAL for both: the absolute
calibration breaches are 2.405pp and 2.338pp beyond the 1pp limit, each
within its approximately 3.247pp SE. RS passes the dev sign check 2/3, but
that cannot cure leg (i).

**Ships:** nothing.
