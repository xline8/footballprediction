# Phase 4 — Model Design: IR Azadegan League candidates

This is a design document only. No model fitting, preregistration,
engine, or virgin read has been performed.

## Shared validation frame

**Dev = 2021/2022 warm-up, scored dev 2022/2023–2024/2025
(n = 884); virgin = 2025/2026 (complete, n = 305 played) read ONCE,
dev-passers only; 2026/2027 partial (n = 68) reserved confirmatory,
never touched.**

Primary line for goals is OU2.5. The frozen descriptive line table:
over-2.5 rate in scored dev is 29.4% pooled (31.6% / 31.7% / 25.2%
by season) — the base-rate baseline is strong in the *under*
direction in every season, which is exactly why the OU2.5 leg is
the binding one. Note the direction is reversed from the
high-scoring leagues (NLTD's 62.4% over-rate): here the model must
beat a baseline that says "under" most of the time. EDA levels of
2025/2026 are design aggregates only and do not set a line, gate,
or arm. The virgin season (1.60 goals/match, 22.6% over-2.5) is
the lowest-scoring complete season in the corpus; the calibration
leg will judge the model against that regime shift, as designed.

## Candidates and feasibility

| candidate | Gate Zero | permitted variant arms | feasibility |
|---|---|---|---|
| G goals | goals-only Dixon-Coles | SHRINK | feasible; no xG blend |
| S SOT | — | — | NOT buildable: no SOT target in any season |
| C corners | — | — | NOT buildable: no corners target in any season |
| K cards | — | — | NOT buildable: no yellows; reds rare (0.085/match, r = 0.07) |
| T total shots | — | — | NOT buildable: no shots target in any season |

Goals arms are exactly Gate Zero (DC goals-only) and SHRINK (frozen
<6 prior-match rating shrink, as the DE-3Liga G prereg). The G-J2
post-mortem lesson is addressed in its SHRINK form: under
season-blocked fitting, prior in-league counts at a season start
are 0 or ≥34 in this league (every club plays a full season or is
absent), so the arm is expected to be bit-identical to Gate Zero
(as in G-NLE, G-ESPF, and G-NLTD); it is run anyway so the fact is
measured, not assumed. There is deliberately **no X2 arm**: the
brief forbids inventing a parent-tier prior, and EDA F4 shows
entrants perform at the league mean (GF +0.002 / GA −0.034), so
there is no entrant parameter to freeze.

## Gates

Dev: an arm passes iff its pooled dev 1X2 LL **and** RPS beat
climatology **and** its OU2.5 LL beats the base-rate baseline, else
FAIL and the virgin is NOT read. Virgin: PASS if LL ≤ best
baseline AND |calibration| ≤ 1pp; PROVISIONAL if breach ≤ 1 SE;
else FAIL. Calibration = actual − predicted. No dev pass => virgin
NOT read.

The halves constant in FEATURES (goals 0.415) is a reporting
constant only; no candidate may fit a team-specific halves model.

## §5 — Persian Gulf flag (carried from DATA_UNDERSTANDING.md §4)

The build brief states Iran has no other league in the warehouse.
The index contradicts that premise: Persian Gulf Pro League (FotMob
id 523) has 1,245 indexed rows across the same six seasons, with
folders on disk. No Persian Gulf data was used in this design —
no feature, no prior, no gate input — and this design does not
depend on it. If the coordinator later authorises an X2 amendment
drawing on that corpus, it requires a fresh prereg (arms, windows,
magnitudes from dev transitions only) committed before any fitting;
it cannot be bolted onto the frozen prereg of this build.
