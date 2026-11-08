# K-NO Verdict — NO-Eliteserien cards model (yellows)

Date: 2026-11-09. Branch `build/no-eliteserien`. Prereg:
`league/NO-Eliteserien/prereg/PREREG_K_NO.md` **as amended**
(commits 48330b5 → 87e8eb1; the amendment header in the prereg is the
full record). Engine: `league/NO-Eliteserien/engine/cards/` (J1 cards
engine seed via AT, re-ported two-arm by the coordinator after the
target amendment). Numbers from the coordinator's own runs.
Predictions-only scope.

## Verdict: PASS (CLEAN) — Gate Zero SHIPS.

Both arms pass the dev gate on the corrected event-unified target,
and X8 is the better dev arm in 2 of 3 seasons — the referee trait
(r=0.316) earns its keep in dev here. On the virgin window the
ranking reverses: X8's LL (0.6540) loses to Gate Zero (0.6379) *and*
to the base rate (0.6509), failing leg (i), while Gate Zero beats
both baselines and lands calibration at −0.84pp — inside the 1.0pp
clean-pass band. **Gate Zero ships, clean.** The shipped predictions
CSV is Gate Zero's.

## The target amendment (summary — prereg header has the record)
The first frozen prereg used the stats-feed yellows and dropped X8
on a stats-feed trait reading (r=0.291). A per-match audit then
proved the stats feed undercounts yellows in every season (corpus
4,353 vs 4,625 event yellows; 171/1,407 matches disagree, 156
stats-low). Target switched to event-unified Yellow+YellowRed before
any virgin read and before any fitting on the corrected target; the
trait on the corrected target reads 0.316, so X8 was restored. The
one discarded stats-target single-arm dev run is not used anywhere.

## Dev results (online walk-forward; scored 2022–2024, n=720)

LL@2.5 (event-unified target):

| Season | n | Gate Zero | X8 | Base rate | Naive t-10 |
|---|---|---|---|---|---|
| 2022 | 240 | 0.6703 | 0.6565 | — | — |
| 2023 | 240 | 0.6628 | 0.6558 | — | — |
| 2024 | 240 | 0.6217 | 0.6247 | — | — |
| **Pooled** | 720 | **0.6516** | **0.6456** | 0.6589 | 0.6566 |

Dev gate: GZ PASS, X8 PASS. Sign check: X8 ≤ GZ in 2/3 seasons — PASS.
Referee coverage in dev: 76.3% (2021 warm-up), 100% (2022–2024).
Dev-stage NB r estimate (2021 warm records): 500 (the estimator's
cap — yellows are near-Poisson here, dispersion 1.06 on the event
target; the virgin-stage fit on 2021–2024 records gives r=157.89).

## Virgin results (season 2025, n=240, read once after dev froze)

Actual over-2.5 rate 64.58%; mean total yellows 3.42 (event target).
Referee coverage 240/240 = 100%; X8 fallbacks: 17 thin-history, 0
unknown-identity.

| Arm | LL@2.5 | Calib diff | Calib SE |
|---|---|---|---|
| Gate Zero | 0.6379 | −0.84pp | 3.05pp |
| X8 | 0.6540 | −0.27pp | 3.10pp |
| Base rate | 0.6509 | — | — |
| Naive t-10 | 0.6599 | — | — |

## Per-leg verdicts

| Leg | Gate Zero | X8 |
|---|---|---|
| Dev gate | PASS | PASS |
| Virgin (i) LL ≤ GZ (0.6379) and ≤ best baseline (0.6509) | PASS | FAIL (0.6540 > both) |
| Virgin (ii) calibration ≤1.0pp (breach ≤1 SE = provisional) | CLEAN PASS (−0.84pp) | CLEAN PASS (−0.27pp) |
| Virgin (iii) dev sign check | n/a | PASS (2/3) |
| **Overall** | **PASS (CLEAN) — SHIPS** | **FAIL** |

The pattern is K-J1's mirror: there the referee arm won dev and lost
the virgin LL leg to naive; here it wins dev and loses the virgin LL
leg to Gate Zero itself. A modest trait (0.316) helping in-sample
seasons and not holding on the virgin is exactly what the gate is
for. Operational note (as K-J1): warehouse records are post-match
snapshots; nothing here proves pre-match referee publication — moot
for the shipped arm, which uses no referee input.

## Verification notes
- Coordinator re-ported this engine directly (two-arm, primary 2.5)
  and diff-audited it against AT: differences are the retargets only,
  plus the CSV-writer line keys fixed to the new ladder.
- One reference-behaviour note: the harness estimates the dev NB r
  from the warm-up season's records — with NO's calendar-year labels
  the J1 warm-up comparison (`season == "2021"`) fires as originally
  designed (in AT's build the same line never matched its
  "2021/2022" labels; recorded here so the cross-league r values are
  not compared naively).
- Predictions CSV halves recomputed for a sample row with the fitted
  r=157.89 from `fitted_params_virgin.json`: 1H P(over 1.5) matches
  NB(0.317·exp_total, 157.89) to 6 decimals.
- The harness's auto-written skeleton verdict was overwritten by
  this file.
