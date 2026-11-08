# S-US Verdict — US-MLS shots-on-target model

Date: 2026-11-09. Branch `build/us-mls`. Prereg: `league/US-MLS/prereg/PREREG_S_US.md` (commit d935f11). Engine: `league/US-MLS/engine/sot/` (J1 SOT seed). Implementation followed the two-agent flow; numbers below are from the frozen coordinator results. Predictions-only scope.

## Verdict: PASS (provisional) — Gate Zero ships.

All four arms pass the dev LL gate, but the harness’s frozen sign-check filter reads only GZ on the virgin: RS fails the sign check 0/3 (its dev LL is worse than GZ in all three seasons), X4 and X6 fail it 1/3, so the harness excludes all three. GZ passes virgin LL and has a calibration breach within one SE, hence provisional pass. (Coordinator correction after verification: an earlier draft of this verdict misstated RS's sign check as 2/3; the dev table below and `results_virgin.json`'s `read_arms: ['GZ']` are authoritative — RS was not read.)

## Dev results (per-match walk-forward; scored 2022–2024, n=1,532)

LL@8.5:

| Season | n | GZ | RS | X4 | X6 | Base rate | Naive t-10 |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2022 | 489 | 0.688941 | 0.689409 | 0.687263 | 0.687263 | 0.689818 | 0.701221 |
| 2023 | 521 | 0.683363 | 0.684281 | 0.686185 | 0.686185 | 0.692280 | 0.696533 |
| 2024 | 522 | 0.666996 | 0.668419 | 0.669232 | 0.671547 | 0.681779 | 0.683611 |
| **Pooled** | **1532** | **0.679567** | **0.680513** | **0.680753** | **0.681541** | **0.687916** | **0.693627** |

Dev gate: GZ/RS/X4/X6 all beat both baselines. Sign check (RS 0/3, X4 1/3, X6 1/3 — a variant must be ≤ GZ in at least 2 of 3 dev seasons) means only GZ is read by the harness; RS/X4/X6 are not read.

## Virgin results (2025, n=540)

Actual over-8.5 rate is 44.63%.

| Arm | LL@8.5 | Mean P(over) | Calibration diff | SE | Actual over-rate |
|---|---:|---:|---:|---:|---:|
| GZ | 0.679882 | 42.49% | −2.14pp | 2.12pp | 44.63% |
| Base rate | 0.681709 | 41.57% | −3.06pp | — | 44.63% |
| Naive t-10 | 0.686402 | 42.81% | −1.82pp | — | 44.63% |

Read arms: `['GZ']`. RS was not read: its sign check is 0/3 (2022: 0.689409 > GZ 0.688941; 2023: 0.684281 > 0.683363; 2024: 0.668419 > 0.666996), so the harness’s frozen read filter excluded it, exactly as it excluded X4/X6 at 1/3.

## Per-leg verdicts

| Leg | GZ | RS | X4 | X6 |
|---|---|---|---|---|
| Dev gate | PASS | PASS | PASS | PASS |
| Virgin (i) LL ≤ GZ and ≤ best baseline (0.681709) | PASS (0.679882) | not read | not read | not read |
| Virgin (ii) calibration ≤1.0pp; breach ≤1 SE provisional | PROVISIONAL PASS (breach 1.14pp ≤ 2.12pp SE) | not read | not read | not read |
| Virgin (iii) dev sign check | n/a | FAIL (0/3) | FAIL (1/3) | FAIL (1/3) |
| **Overall** | **PASS (provisional)** | **not read (filter)** | **FAIL (filter)** | **FAIL (filter)** |

## What ships

GZ. Virgin fitted params: `league/US-MLS/engine/sot/fitted_params_virgin.json` — NB r=79.94; fitted US-MLS league means home 5.1491 and away 4.1075; regression state is persisted in the same file. Predictions: `league/US-MLS/predictions/s_us_virgin_predictions.csv`.

## Verification notes

Virgin isolation used 2025 only for scoring and 2021–2024 as state. The prediction CSV has 540 rows. No goals or cards virgin command was run.
