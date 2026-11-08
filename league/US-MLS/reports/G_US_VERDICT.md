# G-US Verdict — US-MLS goals model

Date: 2026-11-09. Branch `build/us-mls`. Prereg: `league/US-MLS/prereg/PREREG_G_US.md` (commit d935f11). Engine: `league/US-MLS/engine/goals/` (J1 goals seed). Implementation followed the two-agent flow; numbers below are from the frozen coordinator results.

## Verdict: FAIL — at the dev gate. Virgin window NOT read.

Gate Zero and both variants fail the preregistered OU 2.5 dev gate, so the frozen rule makes the variants moot. Nothing ships and no G-US virgin predictions file exists.

## Dev results (season-blocked walk-forward; scored 2022–2024, n=1,532)

OU 2.5 LL (lower is better):

| Season | n | GZ | SHR | X3 | Climatology |
|---|---:|---:|---:|---:|---:|
| 2022 | 489 | 0.700570 | 0.698403 | 0.711463 | 0.683648 |
| 2023 | 521 | 0.686649 | 0.685661 | 0.691395 | 0.688637 |
| 2024 | 522 | 0.692327 | 0.692327 | 0.698247 | 0.673442 |
| **Pooled** | **1532** | **0.693027** | **0.691999** | **0.700135** | **0.681867** |

All arms fail pooled OU: GZ 0.693027, SHR 0.691999, and X3 0.700135 are each above climatology 0.681867.

For the record, pooled 1X2 LL/RPS are GZ 1.067143/0.224753 versus climatology 1.057912/0.222330: climatology beats DC even on 1X2 here. SHR helps marginally (0.6920 versus 0.6930); the expansion-team shrinkage works in the expected direction but cannot close the OU gap. X3 is 0.7001 and hurts despite the strongest ratio trait (r=.684). The goals blend fell back to goals-only for the seven CF Montreal matches lacking xG, per the reference architecture’s own rule.

## Per-leg verdicts

| Leg | GZ | SHR | X3 |
|---|---|---|---|
| Dev gate (pooled OU LL < climatology) | FAIL (0.693027 > 0.681867) | FAIL (0.691999 > 0.681867) | FAIL (0.700135 > 0.681867) |
| Virgin legs | not read | not read | not read |
| **Overall** | **FAIL** | **FAIL (moot)** | **FAIL (moot)** |

## What ships

Nothing.

## Verification notes

Dev outputs were treated as frozen; no goals virgin command was run. The dev loader scored only 2022–2024.
