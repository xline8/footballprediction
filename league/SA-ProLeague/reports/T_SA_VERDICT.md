# Verdict — T-SA (Saudi Pro League total shots) — **PROVISIONAL PASS** (arm A ships)

Prereg: `prereg/PREREG_T_SA.md` (frozen aa3a34d, before fitting).
Dev = walk-forward scored 2023/2024 + 2024/2025 (n=612); virgin =
2025/2026 (n=306), read once for dev-passing arms (all three).

## Dev (pooled LL@24.5)

| Arm | Pooled | 2023/2024 | 2024/2025 | vs baselines (league 0.6973 / naive 0.6730) |
|---|---|---|---|---|
| A (v1 pattern) | 0.6707 | 0.6606 | 0.6807 | beats both — PASS |
| B (v2 level layer) | 0.6681 | 0.6594 | 0.6769 | beats both — PASS |
| C (E9 trailing-r) | 0.6714 | 0.6609 | 0.6820 | beats both — PASS |

## Virgin 2025/2026 (n=306)

| Arm | LL@24.5 | Calibration (SE) |
|---|---|---|
| **A** | **0.6834** | +1.33pp (2.83pp) |
| B | 0.6868 | +1.97pp (2.84pp) |
| C | 0.6833 | +1.31pp (2.83pp) |
| League base rate | 0.6929 | — |
| Naive trailing-10 | 0.6884 | — |

Gate arithmetic: reference arm = A. Leg (i) — A 0.6834 ≤ A ✓ and
≤ best baseline 0.6884 ✓; B 0.6868 > A → leg (i) FAIL; C 0.6833
≤ A ✓ and ≤ baseline ✓. Leg (ii) — A and C both breach 1pp
(1.33 / 1.31pp) but lie within 1 SE (2.83pp) → PROVISIONAL.
Leg (iii) — C's dev LL vs A: 0.6609 > 0.6606 (2023/2024) and
0.6820 > 0.6807 (2024/2025) → 0 of 2 → leg (iii) FAIL for C,
despite its marginally lower virgin LL. Only A passes all legs.

**Ships: arm A** (v1 pattern; fitted params
`engine/total_shots/fitted_params_virgin.json` — r_A 92.31,
level cell [120, 1.0, 50]; predictions
`predictions/t_sa_virgin_predictions.csv`, halves via frozen
0.4559). As with S-SA, every arm over-predicts the virgin total
(the virgin shots level, 24.35/match, ran below the dev 24.65) —
provisional, not clean.
