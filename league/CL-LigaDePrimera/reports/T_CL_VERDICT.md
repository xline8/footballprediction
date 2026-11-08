# Verdict — T-CL (Chile Liga de Primera total shots)

**PASS (clean) — arm A ships.**

## Dev (n = 719, walk-forward 2022–2024, primary line 25.5)

| arm | LL@25.5 |
|---|---|
| A (v1 pattern) | 0.674640 |
| B (v2 level layer) | 0.674741 |
| C (E9 trailing-r) | 0.674868 |
| league base rate | 0.693600 |
| naive trailing-10 | 0.682200 |

All three arms beat both baselines → all read the virgin.

## Virgin (2025, n = 240, read once)

| arm | LL@25.5 | calibration (actual − pred) | SE |
|---|---|---|---|
| A | 0.638337 | −0.647 pp | 3.052 pp |
| B | 0.639689 | −1.121 pp | 3.056 pp |
| C | 0.640646 | +0.202 pp | 3.059 pp |
| league base rate | 0.690002 | — | — |
| naive trailing-10 | 0.643612 | — | — |

Gate arithmetic: leg (i) requires a variant's virgin LL ≤ the
reference arm A's; B (0.639689) and C (0.640646) both exceed A's
0.638337 → **B and C fail leg (i)** (their sign checks are moot).
Arm A: leg (i) 0.638337 ≤ best baseline 0.643612 PASS; leg (ii)
|−0.647 pp| ≤ 1.0 pp → **CLEAN PASS**. A ships.

Virgin numbers recomputed by the coordinator from the shipped
predictions CSV (LL and calibration agree exactly with the
harness JSON). Ships: arm A fitted params
(`engine/total_shots/fitted_params_virgin.json`) + virgin
predictions; 1H/2H presentation via frozen total-shots constant
0.4535.
