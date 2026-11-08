# G-USLL1 Verdict — USL League One goals model

Date: 2026-11-10. Prereg: `prereg/PREREG_G_USLL1.md`. Engine: `engine/goals/`.

## Verdict: FAIL — dev gate; virgin not read

Gate Zero beats climatology on the primary OU 2.5 line but fails the
prereg's additional frozen legs: pooled dev 1X2 LL and RPS are both
worse than climatology. SHR is moot. The virgin window was NOT read and
nothing ships.

## Dev results (2022–2024 regular, n=489)

| Season | n | GZ OU2.5 | SHR OU2.5 | Clim OU2.5 | GZ 1X2 | Clim 1X2 | GZ RPS | Clim RPS |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2022 | 165 | 0.712579 | 0.707321 | 0.693147 | 1.105862 | 1.096490 | 0.233655 | 0.229523 |
| 2023 | 192 | 0.697619 | 0.692899 | 0.691070 | 1.126210 | 1.086534 | 0.244995 | 0.231508 |
| 2024 | 132 | 0.640647 | 0.639024 | 0.684637 | 1.026387 | 1.085489 | 0.213211 | 0.233176 |
| **Pooled** | **489** | **0.687288** | **0.683222** | **0.690034** | **1.092398** | **1.089611** | **0.232589** | **0.231288** |

## Per-leg verdicts

| Leg | GZ | SHR |
|---|---|---|
| OU2.5 LL beats climatology | PASS (0.687288 < 0.690034) | PASS (0.683222; moot) |
| 1X2 LL beats climatology | FAIL (1.092398 > 1.089611) | FAIL (1.094018; moot) |
| RPS beats climatology | FAIL (0.232589 > 0.231288) | FAIL (0.233162; moot) |
| Virgin | not read | not read |
| **Overall** | **FAIL** | **FAIL (moot)** |

The pattern is season-split: the DC model wins clearly in 2024 and
loses in 2022–2023 on every metric. Pooled, the 1X2/RPS legs decide.

## What ships

Nothing. No virgin predictions file exists. Verification: no goals
virgin command was run. Climatology was recomputed independently from
the league CSV (OU 0.690034, 1X2 1.089611 — exact match).
