# T-USLL1 Verdict — USL League One total-shots model

Date: 2026-11-10. Prereg: `prereg/PREREG_T_USLL1.md`. Engine: `engine/total_shots/`.

## Verdict: PASS (provisional) — arm B ships

All three arms pass the 2023–2024 dev gate and the virgin LL leg.
Every arm's virgin calibration breach is within 1 SE (provisional).
Arm C fails the dev sign leg against A (0/2) and is excluded; between
A and B, B has the lower virgin LL and ships.

## Dev results (gate pool 2023–2024 regular, n=321; LL@24.5)

Tuning on 2022 only (n=165): ridge lambda 300.0, r_A = 117.143, arm B
level-layer cell [60, 1.0, 20]. The 2022 season is not in the gate pool.

| Season | n | A | B | C | League base | Naive t-10 |
|---|---:|---:|---:|---:|---:|---:|
| 2023 | 191 | 0.690910 | 0.687267 | 0.691040 | 0.694723 | 0.692157 |
| 2024 | 130 | 0.662921 | 0.667607 | 0.663463 | 0.692959 | 0.672735 |
| **Gate pool** | **321** | **0.679575** | **0.679305** | **0.679872** | **0.694009** | **0.684291** |

All arms beat both baselines. Sign checks versus A: B ≤ A in 2023 only
(1/2, meets the ≥1/2 rule); C ≤ A in neither season (0/2).

## Virgin results (2025 regular, n=210)

Calibration is actual − predicted, in percentage points.

| Arm | LL@24.5 | Mean P(over) | Actual rate | Calibration | SE |
|---|---:|---:|---:|---:|---:|
| A | 0.694820 | 46.529% | 48.571% | +2.045pp | 3.452pp |
| B | 0.693325 | 45.705% | 48.571% | +2.866pp | 3.444pp |
| C | 0.693826 | 46.500% | 48.571% | +2.071pp | 3.449pp |
| League base | 0.696400 | 49.428% | 48.571% | −0.856pp | 3.461pp |
| Naive t-10 | 0.698683 | 45.705% | 48.571% | +2.866pp | 3.459pp |

Read arms: `['A', 'B', 'C']`.

## Per-leg verdicts

| Leg | A | B | C |
|---|---|---|---|
| Dev gate (beats both baselines) | PASS | PASS | PASS |
| Virgin (i) LL ≤ reference A and ≤ best baseline (0.696400) | PASS | PASS (0.693325) | PASS (0.693826) |
| Virgin (ii) calibration ≤1pp; breach ≤1 SE provisional | PROVISIONAL (2.045 ≤ 3.452) | PROVISIONAL (2.866 ≤ 3.444) | PROVISIONAL (2.071 ≤ 3.449) |
| Virgin (iii) dev sign vs A (≥1/2) | n/a (reference) | PASS (1/2) | FAIL (0/2) |
| **Overall** | PASS (provisional) | **PASS (provisional) — ships** | FAIL (leg iii) |

## What ships

Arm B (v2 pattern + level layer). Fitted params:
`engine/total_shots/fitted_params_virgin.json` (r_A = 117.143, level
cell [60, 1.0, 20], half split [0.461, 0.539]). Predictions:
`predictions/t_usll1_virgin_predictions.csv` (210 rows; virgin LL and
calibration recomputed independently from this CSV by the
coordinator — exact match).
