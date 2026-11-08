# T-USL Verdict — USL Championship total-shots model

Date: 2026-11-09. Prereg: `prereg/PREREG_T_USL.md`. Engine: `engine/total_shots/`.

## Verdict: PASS — arm B ships

All three arms pass the 2023–2024 dev gate and all three pass the virgin LL and calibration legs. B has the lowest virgin LL and wins mechanically. B’s sign check versus A is 1/2; C’s is 2/2, satisfying the preregistered ≥1/2 variant rule.

## Dev results (gate pool 2023–2024, n=846; LL@24.5)

| Scope | n | A | B | C | League base | Naive t-10 |
|---|---:|---:|---:|---:|---:|---:|
| 2023 | 423 | 0.658147 | 0.657748 | 0.657819 | 0.687761 | 0.664270 |
| 2024 | 423 | 0.687421 | 0.687805 | 0.686805 | 0.695699 | 0.700609 |
| **Gate pool** | **846** | **0.672784** | **0.672777** | **0.672312** | **0.691730** | **0.682439** |

All arms beat both baselines. Sign checks versus A: B ≤ A in 2023 only (1/2); C ≤ A in both 2023 and 2024 (2/2). The 2022 tuning season is not part of the gate pool.

## Virgin results (2025, n=375)

Calibration is actual − predicted, in percentage points.

| Arm | LL@24.5 | Mean P(over) | Actual rate | Calibration | SE |
|---|---:|---:|---:|---:|---:|
| A | 0.660447 | 40.152% | 38.133% | −2.018pp | 2.494pp |
| B | 0.656916 | 38.725% | 38.133% | −0.592pp | 2.486pp |
| C | 0.659299 | 40.367% | 38.133% | −2.234pp | 2.491pp |
| League base | 0.677092 | 44.184% | 38.133% | −6.051pp | — |
| Naive t-10 | 0.678467 | 37.054% | 38.133% | +1.080pp | — |

Read arms: `['A', 'B', 'C']`.

## Per-leg verdicts

| Leg | A | B | C |
|---|---|---|---|
| Dev gate versus both baselines | PASS | PASS | PASS |
| Virgin (i) LL ≤ reference A (0.660447) and best baseline (0.677092) | PASS | PASS | PASS |
| Virgin (ii) calibration ≤1pp; breach ≤1 SE provisional | PROVISIONAL PASS (2.018pp ≤ 2.494pp) | PASS (0.592pp) | PROVISIONAL PASS (2.234pp ≤ 2.491pp) |
| Virgin (iii) dev sign versus A | n/a | PASS (1/2) | PASS (2/2) |
| **Overall** | **PASS (provisional)** | **PASS — winner** | **PASS (provisional)** |

## What ships

B. Fitted params: `engine/total_shots/fitted_params_virgin.json` — r_A=155.185542, level cell [30, 0.5, 50], half split [0.453, 0.547]. Predictions: `predictions/t_usl_virgin_predictions.csv`.

Verification: the first mandated virgin command exposed and was corrected for two scoped harness defects: the frozen 2025 count was incorrectly asserted as 390 instead of the preregistered 375, and the prediction header omitted `p_over_23_5`. The mandated command was then rerun successfully; no dev output was changed. Coordinator correction after the Codex run: the exported predictions and fitted params originally carried the IT-SerieB half split [0.465, 0.535] and ITB 1H/2H line labels; these were corrected to the frozen USL split [0.453, 0.547] and the preregistered lines (1H 10.5/11.5/12.5; 2H 12.5/13.5/14.5) and the export was regenerated — virgin metrics are byte-identical before and after (arm B, LL@24.5 0.656916).
