# C-US Verdict — US-MLS corners model

Date: 2026-11-09. Branch `build/us-mls`. Prereg: `league/US-MLS/prereg/PREREG_C_US.md` (commit d935f11). Engine: `league/US-MLS/engine/corners/` (J1 corners seed). Implementation followed the two-agent flow; numbers below are from the frozen coordinator results.

## Verdict: PASS (provisional) — Gate Zero ships.

Both arms pass dev. On virgin, both are read; their predictions are identical because both fitted feature multipliers have beta zero. Gate Zero passes LL and has calibration within one SE of the 1pp tolerance. X7 fails the dev sign leg and cannot ship.

## Dev results (season-blocked walk-forward; scored 2022–2024, n=1,532)

LL@9.5:

| Season | n | Gate Zero | X7 | Base rate | Naive t-10 |
|---|---:|---:|---:|---:|---:|
| 2022 | 489 | 0.701607 | 0.717226 | 0.730010 | 0.728978 |
| 2023 | 521 | 0.694795 | 0.697663 | 0.728020 | 0.729212 |
| 2024 | 522 | 0.691867 | 0.691867 | 0.736046 | 0.733489 |
| **Pooled** | **1532** | **0.695972** | **0.701932** | **0.731390** | **0.730595** |

Both arms beat both baselines on pooled LL. X7’s dev sign check is 1/3 (only 2024 is ≤ GZ), so it fails leg (iii).

## Virgin results (2025, n=540)

Actual over-9.5 rate is 48.52%.

| Arm | LL@9.5 | Mean P(over) | Calibration diff | SE | Actual over-rate |
|---|---:|---:|---:|---:|---:|
| Gate Zero | 0.694867 | 49.83% | +1.31pp | 2.16pp | 48.52% |
| X7 | 0.694867 | 49.83% | +1.31pp | 2.16pp | 48.52% |
| Base rate | 0.717480 | 37.58% | −10.94pp | — | 48.52% |
| Naive t-10 | 0.720949 | 36.52% | −12.00pp | — | 48.52% |

Read arms: `['gate_zero', 'x7']`.

## Per-leg verdicts

| Leg | Gate Zero | X7 |
|---|---|---|
| Dev gate | PASS | PASS |
| Virgin (i) LL ≤ GZ and ≤ best baseline (0.717480) | PASS (0.694867) | PASS (tie, 0.694867) |
| Virgin (ii) calibration ≤1.0pp; breach ≤1 SE provisional | PROVISIONAL PASS (breach 0.31pp ≤ 2.16pp SE) | PROVISIONAL PASS (same) |
| Virgin (iii) dev sign check | n/a | FAIL (1/3) |
| **Overall** | **PASS (provisional)** | **FAIL (sign leg)** |

## What ships

Gate Zero. Virgin fitted params: `league/US-MLS/engine/corners/fitted_params_virgin.json` — gamma 0.15, r=1.103217, beta [0,0] for GZ (X7 beta [0]), fit n=1992. Predictions: `league/US-MLS/predictions/c_us_virgin_predictions.csv`.

## Verification notes

The harness selected Gate Zero mechanically after evaluating both arms. The prediction CSV has 540 rows. No goals or cards virgin command was run.
