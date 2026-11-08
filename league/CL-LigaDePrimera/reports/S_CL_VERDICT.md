# Verdict — S-CL (Chile Liga de Primera shots on target)

**PROVISIONAL PASS — arm RS ships.**

## Dev (n = 719, walk-forward 2022–2024, primary line 8.5)

| arm | LL@8.5 |
|---|---|
| Gate Zero | 0.679865 |
| RS (BB prior 200→20,000) | 0.679186 |
| league base rate | 0.695967 |
| naive trailing-10 | 0.682492 |

Both arms beat both baselines → both read the virgin.

## Virgin (2025, n = 240, read once)

| arm | LL@8.5 | calibration (actual − pred) | SE |
|---|---|---|---|
| Gate Zero | 0.670052 | −2.594 pp | 3.156 pp |
| RS | 0.669732 | −2.557 pp | 3.155 pp |
| league base rate | 0.694257 | — | — |
| naive trailing-10 | 0.677311 | — | — |

Gate arithmetic: leg (i) RS 0.669732 ≤ Gate Zero 0.670052 and ≤
best baseline 0.677311 PASS; Gate Zero likewise passes (i).
Leg (ii): |−2.56 pp| and |−2.59 pp| breach the 1.0 pp boundary,
but the excess over the boundary (1.56 / 1.59 pp) is within 1 SE
(3.16 pp) → **PROVISIONAL PASS** for both arms. Leg (iii) for RS:
dev LL ≤ Gate Zero in 2 of 3 seasons (2022, 2024) PASS.
Both-pass rule: lower pooled virgin LL ships → **RS**.

All virgin numbers recomputed by the coordinator from the
per-match prediction CSVs (engine `predictions_virgin.csv` and the
shipped `predictions/s_cl_virgin_predictions.csv` agree exactly).
Ships: RS fitted params (`engine/sot/fitted_params_virgin.json`) +
virgin predictions; 1H/2H presentation via frozen SOT constant
0.4456.
