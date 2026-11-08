# Phase 4 — Model Design: IR Persian Gulf Pro League candidates

This is a design document only. No model fitting, preregistration,
engine, or virgin read has been performed.

## Shared validation frame

**Dev = 2021/2022 warm-up, scored dev 2022/2023–2024/2025
(n = 720); virgin = 2025/2026 league-only (PARTIAL, rounds 1–23,
n = 178) read ONCE, dev-passers only; 2026/2027 partial (n = 105,
18-team expansion, rounds 1–12) reserved confirmatory, never
touched.**

Primary line for goals is OU2.5. The frozen descriptive line table:
over-2.5 rate in scored dev is 32.5% pooled (31.7% / 35.0% / 30.8%
by season) — the base-rate baseline is strong in the *under*
direction in every season, which is exactly why the OU2.5 leg is
the binding one. Note the direction is reversed from the
high-scoring leagues (NLTD's 62.4% over-rate): here the model must
beat a baseline that says "under" most of the time. The same shape
killed the Azadegan sibling's goals model at the dev gate (its OU
0.6337 vs baseline 0.6079); this build starts from that warning.
EDA levels of 2025/2026 are design aggregates only and do not set a
line, gate, or arm. The virgin season (partial, 1.82 goals/match,
28.7% over-2.5) is lower-scoring than scored dev (2.05, 32.5%);
the calibration leg will judge the model against that shift, as
designed — with the disclosed caveat that the virgin covers rounds
1–23 only, so late-season matches are untested until the
confirmatory read.

## Candidates and feasibility

| candidate | Gate Zero | permitted variant arms | feasibility |
|---|---|---|---|
| G goals | goals-only Dixon-Coles | SHRINK, X2 | feasible; no xG blend |
| S SOT | — | — | NOT buildable: no SOT target in any season |
| C corners | — | — | NOT buildable: no corners target in any season |
| K cards | — | — | NOT buildable: yellows exist only in the virgin window (feed break, EDA F6); no dev window |
| T total shots | — | — | NOT buildable: no shots target in any season |

Goals arms are exactly Gate Zero (DC goals-only), SHRINK (frozen
<6 prior-match rating shrink, as the DE-3Liga G prereg), and X2
(frozen entrant offset, defined below). The G-J2 post-mortem lesson
is addressed in its SHRINK form: under season-blocked fitting,
prior in-league counts at a season start are 0 or ≥30 in this
league (every club plays a full 30-match season or is absent), so
the arm is expected to be bit-identical to Gate Zero (as in
G-NLE, G-ESPF, G-NLTD, and G-IRAZ); it is run anyway so the fact
is measured, not assumed.

**X2 definition (frozen, from dev transitions only).** At
prediction time, a team with zero matches in the training window
(an entrant — in dev, exactly the F4 entrants) starts at attack
rating a0 = −0.18 and defence rating d0 = +0.15 instead of the
league mean (0, 0). Derivation: pooled dev entrant gaps GF −0.160
/ GA +0.157 goals per team-match (EDA F4, n = 6 teams, 180
team-matches) at pooled dev team-mean μ = 0.996 goals per
team-match; a0 = ln((μ − 0.160)/μ) = ln(0.839) = −0.175 →
**−0.18**, d0 = ln((μ + 0.157)/μ) = ln(1.158) = +0.146 →
**+0.15** (rounded to 2dp, frozen). Teams with any training-window
match are fitted normally and X2 never touches them; X2 does not
use any Azadegan League data (the rating-based variant is rejected
in FEATURES.md R15). The virgin transition's gaps (−0.038 /
+0.136) are descriptive only and did not enter the frozen values.

## Gates

Dev: an arm passes iff its pooled dev 1X2 LL **and** RPS beat
climatology **and** its OU2.5 LL beats the base-rate baseline, else
FAIL and the virgin is NOT read. Virgin: PASS if LL ≤ best
baseline AND |calibration| ≤ 1pp; PROVISIONAL if breach ≤ 1 SE;
else FAIL. Calibration = actual − predicted. No dev pass => virgin
NOT read.

The halves constant in FEATURES (goals 0.427) is a reporting
constant only; no candidate may fit a team-specific halves model.

## §5 — Azadegan sibling (carried from DATA_UNDERSTANDING.md)

The warehouse index contains a second Iranian league, the Azadegan
League (FotMob id 9372, tier 2, 1,564 rows across the same six
seasons) — the sibling build, completed 2026-11-10 with verdict
0 PASS / 1 FAIL (G-IRAZ failed its dev gate on the OU2.5 leg).
Persian Gulf entrants arrive from that league (2 per season, 3 at
the 2026/2027 expansion). No Azadegan data was used in this design
beyond the *within-league* entrant-gap measurement of EDA F4
(which needs only Persian Gulf scores): no Azadegan feature, no
Azadegan rating, no gate input. If a future amendment wants an
Azadegan-rating mover prior, it requires a fresh prereg (arms,
windows, magnitudes from dev transitions only) committed before
any fitting, and a shipped (passing) Azadegan goals model to draw
ratings from — neither exists today.
