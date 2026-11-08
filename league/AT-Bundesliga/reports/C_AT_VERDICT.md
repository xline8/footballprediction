# C-AT Verdict — AT-Bundesliga corners model

Date: 2026-11-09. Branch `build/at-bundesliga`. Prereg:
`league/AT-Bundesliga/prereg/PREREG_C_AT.md` (commit c6f6cc1).
Engine: `league/AT-Bundesliga/engine/corners/` (J1 corners seed).
Numbers from the coordinator's own runs.

## Verdict: FAIL — both arms fail the virgin calibration leg. Nothing ships.

Both arms pass the dev gate and beat both virgin baselines on LL,
but the virgin season ran cold on corners too (actual over-9.5 rate
42.6% vs dev 51.5%) and both arms over-predict by >5pp — outside
tolerance and outside 1 SE. The predictions CSV on file is the Gate
Zero product (harness fallback, labelled `gate_zero`).

## Dev results (season-blocked walk-forward; scored 2022/2023–2024/2025, n=585)

LL@9.5:

| Season | n | Gate Zero | X7 | Base rate | Naive t-10 |
|---|---|---|---|---|---|
| 2022/2023 | 195 | 0.6786 | 0.6895 | 0.7512 | 0.7469 |
| 2023/2024 | 195 | 0.7062 | 0.6933 | 0.7247 | 0.7350 |
| 2024/2025 | 195 | 0.6982 | 0.6936 | 0.7208 | 0.7275 |
| **Pooled** | 585 | **0.6943** | **0.6921** | 0.7322 | 0.7365 |

Dev gate: GZ PASS, X7 PASS (both beat both baselines). Sign check:
X7 ≤ GZ in 2/3 seasons — PASS.

## Virgin results (season 2025/2026, n=195, read once after dev froze)

Actual over-9.5 rate 42.56%; mean total corners 9.33.

| Arm | LL@9.5 | Mean P(over 9.5) | Calib diff | Calib SE |
|---|---|---|---|---|
| Gate Zero | 0.6785 | 47.85% | +5.29pp | 3.52pp |
| X7 | 0.6819 | 47.94% | +5.37pp | 3.53pp |
| Base rate | 0.6882 | 37.15% | −5.41pp | — |
| Naive t-10 | 0.6912 | 36.32% | −6.24pp | — |

## Per-leg verdicts

| Leg | Gate Zero | X7 |
|---|---|---|
| Dev gate | PASS | PASS |
| Virgin (i) LL ≤ GZ (0.6785) and ≤ best baseline (0.6882) | PASS | FAIL (0.6819 > 0.6785) |
| Virgin (ii) calibration ≤1.0pp (breach ≤1 SE = provisional) | FAIL (breach 4.29pp > SE 3.52pp) | FAIL (breach 4.37pp > SE 3.53pp) |
| Virgin (iii) dev sign check | n/a | PASS (2/3) |
| **Overall** | **FAIL** | **FAIL** |

The X7 finding replicates C-J1 exactly: the box-touch trait is the
most reliable measured in this EDA (r=0.945), yet the multiplier's
fitted beta is **0 in every fit** — dev seasons and the virgin fit
alike (`active_with_nonzero_beta_share` = 0.0 throughout; on the
virgin fit beta = [0.0]). Inside this multiplier structure the trait
earns nothing; X7's dev edge came from the bare ratings part of its
predictions, and on the virgin it is worse than Gate Zero. Recorded
as a result, not a tuning invitation.

## Verification notes
- Coordinator ran dev and virgin steps. The beta=0 mechanism was
  verified in `core.py` (grid search with the seed's frozen
  tie-break) and in the results JSONs' diagnostics, not inferred
  from the LLs. Virgin isolation: dev season set in code excludes
  2025/2026 and 2026/2027.
