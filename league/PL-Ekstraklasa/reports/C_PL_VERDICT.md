# C-PL verdict

Preregistration: `prereg/PREREG_C_PL.md`; virgin is 2025/2026, n=306, read once. Calibration is actual − predicted.

## Dev primary-line table (LL@9.5)

| arm / baseline | 2022/23 | 2023/24 | 2024/25 | pooled |
|---|---:|---:|---:|---:|
| Gate Zero | 0.699518 | 0.696668 | 0.679903 | 0.692029 |
| X7 | 0.699518 | 0.688648 | 0.679903 | 0.689356 |
| league base rate | — | — | — | 0.735054 |
| naive trailing-10 | — | — | — | 0.738672 |

Both arms pass the dev gate. The X7 sign check versus Gate Zero is tie, better, tie: 3/3 (≥2/3).

## Virgin table

| arm / baseline | LL@9.5 | actual over % | mean predicted % | calibration pp ± SE |
|---|---:|---:|---:|---:|
| Gate Zero | 0.702169 | 49.020 | 52.975 | −3.956 ± 2.880 |
| X7 | 0.696093 | 49.020 | 52.979 | −3.959 ± 2.862 |
| league base rate | 0.716889 | 49.020 | 38.243 | +10.777 ± — |
| naive trailing-10 | 0.723780 | 49.020 | 37.437 | +11.582 ± — |

## Gate arithmetic

- Gate Zero: leg (i) **PASS** (0.702169 ≤ 0.702169 and ≤ 0.716889); leg (ii) **FAIL** (3.956 pp > 1.0 pp + 2.880 pp); leg (iii) exempt.
- X7: leg (i) **PASS** (0.696093 ≤ 0.702169 and ≤ 0.716889); leg (ii) **FAIL** (3.959 pp > 1.0 pp + 2.862 pp); leg (iii) **PASS**, 3/3.

X7 both-teams-active share by scored season was 42.5%, 50.0%, 92.8%; virgin activity was 92.5%. Its fitted beta was zero in the virgin, so active windows did not produce a nonzero multiplier. C-PL verdict: **FAIL; nothing ships**. Prediction CSV: none. Fitted params: none. Verification: coordinator cross-checked results_virgin.json (GZ LL@9.5 0.702169, X7 0.696093, calibration −3.956/−3.959 pp, SEs 2.880/2.862) and the virgin actual over-9.5 rate from the data CSV (49.02%). The calibration failure is narrow — the breach exceeds the boundary by 2.956 pp against an SE of 2.880 pp (GZ) — but the gate is mechanical and does not move.
