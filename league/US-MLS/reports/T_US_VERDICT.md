# T-US Verdict — US-MLS total-shots model

Date: 2026-11-09. Branch `build/us-mls`. Prereg: `league/US-MLS/prereg/PREREG_T_US.md` (commit d935f11). Engine: `league/US-MLS/engine/total_shots/` (J1 total-shots seed; arms A and C only). Implementation followed the two-agent flow; numbers below are from the frozen coordinator results.

## Verdict: PASS — arm C ships.

Both arms pass the gate-pool dev gate and both virgin legs. C wins virgin LL and also passes the gate-pool sign check (2/2).

## Dev results (gate pool 2023–2024, n=1,043; primary line 25.5)

| Scope | n | A | C | League base | Naive t-10 |
|---|---:|---:|---:|---:|---:|
| 2023 | 521 | 0.654262 | 0.653818 | 0.688582 | 0.664490 |
| 2024 | 522 | 0.677215 | 0.677156 | 0.693708 | 0.684565 |
| **Gate pool** | **1043** | **0.665750** | **0.665498** | **0.691147** | **0.674537** |

Dev gate: A and C beat both baselines. C ≤ A in 2/2 gate-pool seasons.

## Virgin results (2025, n=540)

Actual over-25.5 rate is 47.41%.

| Arm | LL@25.5 | Mean P(over) | Calibration diff | SE | Actual over-rate |
|---|---:|---:|---:|---:|---:|
| A | 0.678964 | 48.40% | +0.99pp | 2.12pp | 47.41% |
| C | 0.678127 | 48.22% | +0.81pp | 2.12pp | 47.41% |
| League base | 0.694147 | 49.95% | +2.54pp | — | 47.41% |
| Naive t-10 | 0.691358 | 48.52% | +1.11pp | — | 47.41% |

Read arms: `['A', 'C']`.

## Per-leg verdicts

| Leg | A | C |
|---|---|---|
| Dev gate (gate pool) | PASS | PASS |
| Virgin (i) LL ≤ A and ≤ best baseline (0.691358) | PASS (0.678964) | PASS (0.678127) |
| Virgin (ii) calibration ≤1.0pp; breach ≤1 SE provisional | PASS (0.99pp) | PASS (0.81pp) |
| Virgin (iii) dev sign check | n/a | PASS (2/2) |
| **Overall** | **PASS** | **PASS — winner** |

## What ships

C. Frozen fitted params: `league/US-MLS/engine/total_shots/fitted_params.json` — lambda 100, r_A 109.1951, level cell [30, 0.5, 50], trailing-r window 200, half split [0.456, 0.544], primary line 25.5. Predictions: `league/US-MLS/predictions/t_us_virgin_predictions.csv`.

## Verification notes

The T virgin runner’s stale assertion was corrected from 195 to the repository’s actual 2025 season size, 540; no dev run or dev output was changed. The prediction CSV has 540 rows. No goals or cards virgin command was run.
