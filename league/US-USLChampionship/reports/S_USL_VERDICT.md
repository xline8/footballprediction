# S-USL Verdict — USL Championship shots-on-target model

Date: 2026-11-09. Prereg: `prereg/PREREG_S_USL.md`. Engine: `engine/sot/`.

## Verdict: PASS (provisional) — Gate Zero ships

Both arms pass the dev LL gate. The frozen sign leg reads only GZ on virgin: RS is worse than GZ in all three scored dev seasons (0/3). GZ passes virgin LL and its calibration breach is within one SE.

## Dev results (2022–2024, n=1,318; LL@8.5)

| Season | n | GZ | RS | League base | Naive t-10 |
|---|---:|---:|---:|---:|---:|
| 2022 | 472 | 0.665039 | 0.665398 | 0.692942 | 0.668915 |
| 2023 | 423 | 0.681301 | 0.681537 | 0.696971 | 0.697919 |
| 2024 | 423 | 0.692568 | 0.693030 | 0.693805 | 0.697676 |
| **Pooled** | **1318** | **0.679094** | **0.679446** | **0.694512** | **0.687454** |

Both arms beat both baselines. RS sign check fails: 2022 0.665398 > 0.665039, 2023 0.681537 > 0.681301, 2024 0.693030 > 0.692568.

## Virgin results (2025, n=375)

Calibration below is actual − predicted; the runner stores the opposite-signed `calibration_diff`.

| Arm | LL@8.5 | Mean P(over) | Actual rate | Calibration | SE |
|---|---:|---:|---:|---:|---:|
| GZ | 0.666507 | 40.760% | 38.400% | −2.360pp | 2.514pp |
| League base | 0.689239 | 49.125% | 38.400% | −10.725pp | — |
| Naive t-10 | 0.682156 | 38.129% | 38.400% | +0.271pp | — |

Read arms: `['GZ']`. RS was excluded by the frozen 0/3 sign check.

## Per-leg verdicts

| Leg | GZ | RS |
|---|---|---|
| Dev LL beats both baselines | PASS | PASS |
| Virgin (i) LL ≤ GZ and best baseline (0.682156) | PASS (0.666507) | not read |
| Virgin (ii) | PROVISIONAL PASS (2.360pp breach ≤ 2.514pp SE) | not read |
| Virgin (iii) dev sign | n/a | FAIL (0/3) |
| **Overall** | **PASS (provisional)** | **FAIL (sign/read filter)** |

## What ships

GZ. Fitted params: `engine/sot/fitted_params_virgin.json` (NB r=79.94; league means home 4.4691, away 3.6452; regression state persisted). Predictions: `predictions/s_usl_virgin_predictions.csv` (375 rows). Coordinator correction after the Codex run: the ported harness originally wrote this file under the US-MLS name `s_us_virgin_predictions.csv` and with the MLS halves split 0.450/0.550 in its 1H/2H ladders; the filename and the frozen USL split 0.456/0.544 were corrected and the export regenerated — virgin metrics are byte-identical before and after (GZ LL@8.5 0.666507).

Verification: `python3 run_s_usl.py virgin-metrics`, then `python3 run_s_usl.py virgin-predict --arm GZ`.
