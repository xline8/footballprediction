# S-AT Verdict — AT-Bundesliga shots-on-target model

Date: 2026-11-09. Branch `build/at-bundesliga`. Prereg:
`league/AT-Bundesliga/prereg/PREREG_S_AT.md` (commit c6f6cc1).
Engine: `league/AT-Bundesliga/engine/sot/` (J1 SOT engine seed; the
X6/xGOT arm was deleted with the trait — FEATURES F7). Numbers from
the coordinator's own runs. Predictions-only scope.

## Verdict: FAIL — every arm fails a virgin leg. Nothing ships.

All three arms pass the dev gate. On the virgin window the season ran
cold (actual over-8.5 rate 34.4% vs dev 48.2%; mean SOT 7.93 vs dev
8.58) and every model over-predicted by ~7.7pp — far outside the
calibration tolerance. The virgin predictions CSV on file is the
Gate Zero product, labelled `arm = GZ`, per the prereg fallback.

## Dev results (per-match walk-forward; scored 2022/2023–2024/2025, n=585)

LL@8.5:

| Season | n | GZ | RS | X4 | Base rate | Naive t-10 |
|---|---|---|---|---|---|---|
| 2022/2023 | 195 | 0.6931 | 0.6922 | 0.6907 | — | — |
| 2023/2024 | 195 | 0.6804 | 0.6804 | 0.6813 | — | — |
| 2024/2025 | 195 | 0.6924 | 0.6925 | 0.6951 | — | — |
| **Pooled** | 585 | **0.6886** | **0.6884** | **0.6891** | 0.6953 | 0.6986 |

Dev gate (pooled LL@8.5 beats BOTH baselines): GZ PASS, RS PASS,
X4 PASS. Sign check (leg iii): RS 2/3 seasons ≤ GZ — PASS; X4 1/3 —
**FAIL**, so the harness's frozen read filter did not read X4 on the
virgin window (recorded here mechanically; X4 cannot ship).

## Virgin results (season 2025/2026, n=195, read once after dev froze)

Actual over-8.5 rate 34.36%; mean total SOT 7.93.

| Arm | LL@8.5 | Mean P(over 8.5) | Calib diff | Calib SE |
|---|---|---|---|---|
| Gate Zero | 0.6545 | 42.07% | +7.70pp | 3.41pp |
| RS | 0.6532 | 42.11% | +7.74pp | 3.40pp |
| Base rate | 0.6826 | 48.21% | +13.85pp | — |
| Naive t-10 | 0.6541 | 40.07% | +5.73pp | — |

## Per-leg verdicts

| Leg | Gate Zero | RS | X4 |
|---|---|---|---|
| Dev gate | PASS | PASS | PASS |
| Virgin (i) LL ≤ GZ (0.6545) and ≤ best baseline (0.6541) | FAIL (0.6545 > 0.6541) | PASS (0.6532) | not read |
| Virgin (ii) calibration ≤1.0pp (breach ≤1 SE = provisional) | FAIL (breach 6.70pp > SE 3.41pp) | FAIL (breach 6.74pp > SE 3.40pp) | not read |
| Virgin (iii) dev sign check | n/a | PASS (2/3) | FAIL (1/3) |
| **Overall** | **FAIL** | **FAIL** | **FAIL** |

The failure is a level failure, not a ranking failure: both read
arms beat the base rate on LL and RS beats every baseline, but the
whole league's SOT level dropped in 2025/2026 and the walk-forward's
decayed state (HL 365) carried the old level for most of the season.
That is precisely what the calibration leg exists to catch.

## Verification notes
- Coordinator ran dev and virgin steps; the predictions CSV's halves
  ladders were recomputed by hand for a sample row (1H P(over 3.5)
  and 2H P(over 4.5) match NB(0.447·exp, r=79.94) / NB(0.553·exp)
  to 4 decimals).
- Arm activation: RS and X4 dev LLs differ from GZ on the pooled and
  per-season rows (no silent fallback). Virgin isolation: the dev
  loader's season set excludes 2025/2026 and 2026/2027 in code.
