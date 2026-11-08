# K-J1 Verdict — J1 cards model

Date: 2026-11-09. Branch `build/k-j1`. Prereg:
`league/J1/prereg/PREREG_K_J1.md` (commit dc78d70, frozen before any
fitting). Engine: `league/J1/engine/cards/`. Implementation by Codex
(gpt-5.6-luna) under the two-agent flow; all numbers below were
reproduced end-to-end by the coordinator's own rerun (dev and virgin
JSONs and the predictions CSV identical), and 5 virgin predictions
were recomputed by hand with independent NB code (max diff 5e-14).

## Verdict: FAIL — no arm passes all gate legs, nothing ships

Both arms pass the dev gate, and on dev the referee arm X8 is
genuinely better than Gate Zero (pooled LL@2.5 0.6785 vs 0.6872).
On the virgin window, however, both arms lose virgin leg (i) to the
naive trailing-10 baseline (0.6807): Gate Zero scores 0.6829 and X8
0.6831. Per the frozen both-pass rule, K-J1 does not ship. The
virgin predictions CSV on file is the Gate Zero fallback, labelled
`arm = gate_zero`, for the record only.

A structural caveat sits underneath the X8 virgin number: referee
identity is present for exactly **1 of the 200** virgin matches, so
X8's virgin score is Gate Zero on 199 matches plus one adjusted
match (multiplier 1.0242), scored with its own NB size. The virgin
window effectively cannot test the referee arm — see the
operational check below.

## Dev results (online walk-forward, warm-up 2021; scored 2022–2025, pooled n = 1,372)

NB size r (from 2021 causal residuals, frozen): Gate Zero model
11.29, X8 model 13.17, base rate 9.05, naive 10.75.

| Season | n | Gate Zero LL@2.5 | X8 LL@2.5 | Base LL@2.5 | Naive LL@2.5 |
|---|---|---|---|---|---|
| 2022 | 306 | 0.6706 | 0.6638 | 0.6840 | 0.6780 |
| 2023 | 306 | 0.7043 | 0.6838 | 0.7292 | 0.6893 |
| 2024 | 380 | 0.6931 | 0.6837 | 0.6910 | 0.7018 |
| 2025 | 380 | 0.6808 | 0.6810 | 0.6868 | 0.6853 |
| Pooled | 1372 | 0.6872 | 0.6785 | 0.6968 | 0.6891 |

Context, LL@3.5 pooled: Gate Zero 0.5632, X8 0.5620, base 0.5675,
naive 0.5640. Dev gate (pooled LL@2.5 must beat BOTH baselines):
Gate Zero **PASS**, X8 **PASS**.

X8 fallbacks on dev (pooled): unknown identity 631, thin history
113 — the covariate was actually active on 628 of 1,372 matches
(45.8%), and still produced the pooled improvement above. Per-season
sign check (X8 LL ≤ Gate Zero): 2022 ✓, 2023 ✓, 2024 ✓, 2025 ✗
(0.6810 vs 0.6808, worse by 0.0002) → 3 of 4, **PASS** (≥ half
required).

## Virgin results (season "2026", n = 200, read once after dev froze)

Actuals: mean yellows 2.35/match, over-2.5 rate 42.5%. NB size r
re-estimated on 2021–2025 causal residuals: Gate Zero model 307.68,
X8 model 500.0 (clip), base 53.99, naive 500.0 (clip).

| Arm | LL@2.5 | LL@3.5 | Mean P(over 2.5) | Calib diff | SE |
|---|---|---|---|---|---|
| Gate Zero | 0.6829 | 0.5261 | 44.47% | +1.97pp | 3.50pp |
| X8 | 0.6831 | 0.5262 | 44.50% | +2.00pp | 3.50pp |
| Base rate | 0.6834 | 0.5216 | 43.76% | — | — |
| Naive trailing-10 | 0.6807 | 0.5302 | 43.27% | — | — |

## Per-leg verdicts

| Leg | Gate Zero | X8 |
|---|---|---|
| Dev gate | PASS | PASS |
| Virgin LL (i) (≤ Gate Zero and ≤ best baseline 0.6807) | FAIL (0.6829 > 0.6807) | FAIL (0.6831 > 0.6829 and > 0.6807) |
| Calibration (ii) (≤1.0pp, or breach ≤1 SE = provisional) | PROVISIONAL PASS (breach 0.97pp ≤ SE 3.50pp) | PROVISIONAL PASS (breach 1.00pp ≤ SE 3.50pp) |
| Per-season sign check (iii) | n/a (comparator) | PASS (3/4) |
| **Overall** | **FAIL** | **FAIL** |

The naive trailing-10 baseline is the leg-(i) winner on this
window. Its virgin r hit the 500 clip (near-Poisson), and the 2026
transitional season's card level (2.35/match) sat close to the
recent trailing level the naive baseline tracks, while the decayed
ratings arms carried a slightly higher mean prediction (44.5%
predicted over rate vs 42.5% actual). The gate is mechanical and is
applied as written; no arm ships.

## Operational check — pre-match referee availability (required section)

Referee identity was extracted from
`content.matchFacts.infoBox.Referee.text` in the warehouse JSONs
into `league/J1/engine/cards/referee_table.csv` (2,091 matches).
Coverage of completed-match records:

| Season | With referee | n | Fraction |
|---|---|---|---|
| 2021 | 216 | 380 | 56.8% |
| 2022 | 194 | 306 | 63.4% |
| 2023 | 165 | 306 | 53.9% |
| 2024 | 217 | 380 | 57.1% |
| 2025 | 165 | 380 | 43.4% |
| 2026 (virgin) | 1 | 200 | 0.5% |
| 2026/2027 | 121 | 139 | 87.1% |
| **All** | **1,079** | **2,091** | **51.6%** |

(Dev period 2021–2025: 957/1,752 = 54.6%. The Referee key is
present in essentially every record; in the missing cases its text
is empty.)

What this can and cannot prove, stated plainly:

- Historical data **can** prove that a referee identity is attached
  to about half of completed J1 match records in this warehouse,
  with wild season-to-season variation (0.5% to 87.1%).
- Historical data **cannot** prove that an appointment was
  published before kickoff for any fixture. The warehouse records
  are post-match snapshots with no publication timestamp; a name
  present after the match says nothing about when it became known.
  The near-total absence in the completed 2026 season (1/200),
  against 87.1% in the in-progress 2026/27 season, underlines that
  presence in the record is a property of the snapshot/feed, not
  evidence of pre-match availability.
- Operating rule (as frozen in the prereg and implemented): a
  fixture whose referee is unknown, or whose referee has fewer
  than 8 prior in-league matches, falls back to the base arm
  (Gate Zero) for that fixture. No referee is ever imputed. Under
  current coverage that rule would make X8 inactive for the large
  majority of fixtures even if the arm had passed.

## Verification notes (coordinator, independent of Codex)

- Full harness rerun reproduces every dev and virgin number, the
  fitted parameters, and the predictions CSV exactly.
- Virgin isolation confirmed in code: the dev path loads only
  seasons 2021–2025; season "2026" is touched only by the virgin
  step, and the virgin runner only reads arms that passed the dev
  gate (both did).
- Referee causality: the engine filters referee history to kickoffs
  strictly before the target kickoff and asserts it in code; the
  coordinator independently recomputed trailing histories from
  `referee_table.csv` + the matches CSV — for the one virgin match
  with a known referee (match 5130398, Koji Takasaki), n_prior = 15
  and the X8 multiplier 1.0242 reproduce exactly, and no counted
  match has kickoff ≥ the target's. Referee-table spot checks
  against raw warehouse JSONs match, including empty-text cases.
- Spot check: 5 virgin predictions recomputed by hand from the
  CSV's expected totals and the fitted r (own NB code) match the
  FT ladder exactly; 1H/2H means equal the 0.383/0.617 frozen split
  and the half lines equal the split-mean NB values.
- The predictions CSV is Gate Zero's: its `multiplier` column is
  1.0 throughout (Gate Zero applies no referee adjustment) and its
  referee columns are the extracted identity / prior count for the
  record only.
- Coordinator corrections to Codex's auto-drafted verdict, neither
  changing any model number: (1) its leg-(i) check compared only
  against the base-rate baseline and missed the naive baseline —
  the naive baseline (0.6807) is in fact the best virgin baseline,
  so both arms fail leg (i), not just X8; (2) its provisional-pass
  test used |diff| ≤ SE instead of the prereg's breach-within-1-SE
  test — both arms pass under either reading here, and this verdict
  applies the prereg's rule. Also noted: the engine's league-mean
  fallback also triggers on a zero-card opening observation
  (production would divide by zero there); disclosed in the engine
  README, confined to the first warm-up matches.
