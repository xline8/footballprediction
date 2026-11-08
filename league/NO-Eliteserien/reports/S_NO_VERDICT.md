# S-NO Verdict — NO-Eliteserien shots-on-target model

Date: 2026-11-09. Branch `build/no-eliteserien`. Prereg:
`league/NO-Eliteserien/prereg/PREREG_S_NO.md` (commit 48330b5).
Engine: `league/NO-Eliteserien/engine/sot/` (J1 SOT engine seed via
AT; no X6 arm — the xGOT era starts in the virgin season, F7).
Numbers from the coordinator's own runs. Predictions-only scope.

## Verdict: FAIL — both read arms fail the virgin calibration leg. Nothing ships.

All three arms pass the dev gate. X4 then fails the dev sign check
(0/3 seasons ≤ Gate Zero) and is **not read** on the virgin, per the
frozen filter. On the virgin window the season ran hot (actual
over-8.5 rate 57.9% vs dev 52.5%; mean SOT 9.28 vs dev 8.98) and both
read arms under-predicted by ~6.2pp — far outside the calibration
tolerance. The virgin predictions CSV on file is the Gate Zero
product, labelled `arm = GZ`, per the prereg fallback.

## Dev results (per-match walk-forward; scored 2022–2024, n=720)

LL@8.5:

| Season | n | GZ | RS | X4 | Base rate | Naive t-10 |
|---|---|---|---|---|---|---|
| 2022 | 240 | 0.6804 | 0.6827 | 0.6869 | — | — |
| 2023 | 240 | 0.6811 | 0.6794 | 0.6820 | — | — |
| 2024 | 240 | 0.7016 | 0.7002 | 0.7031 | — | — |
| **Pooled** | 720 | **0.6877** | **0.6874** | **0.6907** | 0.6944 | 0.6991 |

Dev gate (pooled LL@8.5 beats BOTH baselines): GZ PASS, RS PASS,
X4 PASS. Sign check (leg iii): RS 2/3 seasons ≤ GZ — PASS; X4 0/3 —
**FAIL**, so X4 was not read on the virgin window (recorded here
mechanically; X4 cannot ship). Note the league difference the prereg
flagged: with the on-target-rate trait reliable here (F6 r=0.477),
RS — the arm that shrinks that trait away — was *not* the dev
favourite it was in J1/AT; its dev edge over GZ is 0.0003, a tie in
substance.

## Virgin results (season 2025, n=240, read once after dev froze)

Actual over-8.5 rate 57.92%; mean total SOT 9.28.

| Arm | LL@8.5 | Mean P(over 8.5) | Calib diff | Calib SE |
|---|---|---|---|---|
| Gate Zero | 0.6496 | 51.80% | −6.12pp | 3.07pp |
| RS | 0.6483 | 51.70% | −6.21pp | 3.06pp |
| Base rate | 0.6865 | 52.50% | −5.42pp | — |
| Naive t-10 | 0.6623 | 52.01% | −5.91pp | — |

## Per-leg verdicts

| Leg | Gate Zero | RS | X4 |
|---|---|---|---|
| Dev gate | PASS | PASS | PASS |
| Virgin (i) LL ≤ GZ (0.6496) and ≤ best baseline (0.6623) | PASS | PASS (0.6483) | not read |
| Virgin (ii) calibration ≤1.0pp (breach ≤1 SE = provisional) | FAIL (breach 5.12pp > SE 3.07pp) | FAIL (breach 5.21pp > SE 3.06pp) | not read |
| Virgin (iii) dev sign check | n/a | PASS (2/3) | FAIL (0/3) |
| **Overall** | **FAIL** | **FAIL** | **FAIL** |

The failure is a level failure, not a ranking failure: both read arms
beat every baseline on LL (RS is the best number on the window), but
the league's SOT level rose in 2025 and the walk-forward's decayed
state carried the old level — the mirror image of AT's cold-virgin
failure, and precisely what the calibration leg exists to catch.

## Verification notes
- Coordinator reran dev; pooled LLs match the implementer's run to
  6 decimals; pooled = mean of season LLs (equal n), checked.
- Halves ladders in the predictions CSV recomputed independently for
  a sample row: 1H P(over 3.5) matches NB(0.456·exp_total, r=79.94)
  to 6 decimals. Actuals in the CSV reproduce the virgin CSV totals
  (mean SOT 9.275 both ways).
