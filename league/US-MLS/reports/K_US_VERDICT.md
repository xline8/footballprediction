# K-US Verdict — US-MLS cards model (yellows)

Date: 2026-11-09. Branch `build/us-mls`. Prereg: `league/US-MLS/prereg/PREREG_K_US.md` (commit d935f11). Engine: `league/US-MLS/engine/cards/` (J1 cards seed). Implementation followed the two-agent flow; numbers below are from the frozen coordinator results. Primary line: 4.5.

## Verdict: FAIL — at the dev gate. Virgin window NOT read.

Gate Zero fails its own dev gate, so X8 is moot even though it passes the pooled dev comparison. Nothing ships and no K-US virgin predictions file exists.

## Dev results (per-match walk-forward; scored 2022–2024, cards n=1,529)

LL@4.5:

| Season | n | GZ | X8 | Base rate | Naive t-10 |
|---|---:|---:|---:|---:|---:|
| 2022 | 486 | 0.706163 | 0.714217 | 0.684875 | 0.684033 |
| 2023 | 521 | 0.676576 | 0.666706 | 0.683755 | 0.699059 |
| 2024 | 522 | 0.654393 | 0.634751 | 0.663316 | 0.665172 |
| **Pooled** | **1529** | **0.678407** | **0.670898** | **0.677134** | **0.682714** |

Gate Zero fails: 0.678407 is above the base rate 0.677134, although it beats naive 0.682714. X8 passes at 0.670898, but is moot under the frozen gate order.

The prereg’s “100% coverage” sentence was wrong. Stats-feed yellows are missing for seven CF Montreal matches in 2021–2022, giving 99.15%/99.39% coverage in those seasons and 100% from 2023. Event counts were not used. This correction is recorded here and in the coordinator-fix commit; the gates are unchanged.

Virgin referee coverage is 96.1%. Unlike K-J1/K-AT, X8 would have been testable; the frozen rule still applies plainly: Gate Zero fails, so X8 is not read.

## Per-leg verdicts

| Leg | GZ | X8 |
|---|---|---|
| Dev gate (pooled LL beats both baselines) | FAIL (0.678407 > base 0.677134) | PASS (0.670898) — moot |
| Virgin legs | not read | not read (rule) |
| **Overall** | **FAIL** | **FAIL (moot)** |

## What ships

Nothing.

## Verification notes

Dev outputs were treated as frozen; no cards virgin command was run. The coordinator-fix exclusion yields scored dev n=1,529; pre-fix GZ/X8 were 0.678478/0.671134 and the verdict was unchanged.
