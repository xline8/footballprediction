# K-CY verdict — FAIL — nothing ships

Prereg: `prereg/PREREG_K_CY.md`, frozen 2026-11-10. Primary line **4.5**;
virgin 2025/2026 n = **240**; calibration is actual minus predicted.

## Dev results — pooled LL@4.5

| Arm / baseline | LL |
|---|---:|
| Gate Zero | 0.689344 |
| League base rate | 0.693217 |
| Naive trailing-10 | 0.692315 |

Gate Zero beats both baselines and passes the dev gate.

## Virgin results — 2025/2026

| Arm / baseline | LL@4.5 | actual − mean P | SE |
|---|---:|---:|---:|
| Gate Zero | 0.711175 | −2.569pp | 3.286pp |
| League base rate | 0.695157 | — | — |
| Naive trailing-10 | 0.699365 | — | — |

## Gate arithmetic

Leg (i) fails: 0.711175 > best baseline 0.695157. Leg (ii) is
PROVISIONAL: the 1pp calibration limit is breached by 1.569pp, within the
3.286pp SE. There is no variant leg, but the failed LL leg means nothing
ships.

**Ships:** nothing.
