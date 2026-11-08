# Phase 4 — model design sketch (not fitted)

This is a design document only. No model fitting, preregistration,
engine, or virgin read has been performed.

## Shared validation frame

**Dev = 2021/2022 warm-up, scored dev 2022/2023–2024/2025
(n = 918); virgin = 2025/2026 (complete, n = 306) read ONCE,
dev-passers only; 2026/2027 partial reserved confirmatory, never
touched.**

Primary line for goals is OU2.5. The frozen descriptive DEV line
table: over-2.5 rate in scored dev is 62.4% pooled (59.5% /
61.1% / 62.1% / 64.1% by season) — the base-rate baseline is strong
in every season, which is exactly why the OU2.5 leg is the binding
one. EDA levels of 2025/2026 are design aggregates only and do not
set a line, gate, or arm.

## Candidates and feasibility

| candidate | Gate Zero | permitted variant arms | feasibility |
|---|---|---|---|
| G goals | goals-only Dixon-Coles | SHRINK; X2 below-tier entrant prior | feasible; no xG blend |
| S SOT | — | — | NOT buildable: no SOT target in any season |
| C corners | — | — | NOT buildable: no corners target in any season |
| K cards | — | — | NOT buildable: no yellows; reds rare (0.145/match, r = −0.09) |
| T total shots | — | — | NOT buildable: no shots target in any season |

Goals arms are exactly Gate Zero (DC goals-only), SHRINK (frozen
<6 prior-match rating shrink, as the DE-3Liga G prereg), and X2
(below-tier entrant prior, FEATURES-adopted with frozen dev-only
magnitudes GF −0.093 / GA +0.181). The G-J2 post-mortem lesson
applies here in its X2 form: newcomer ratings need a prior rather
than the league mean, and this design names it before fitting.

## Gates

Dev: an arm passes iff its pooled dev 1X2 LL **and** RPS beat
climatology **and** its OU2.5 LL beats the base-rate baseline, else
FAIL and the virgin is NOT read. Virgin: PASS if LL ≤ best
baseline AND |calibration| ≤ 1pp; PROVISIONAL if breach ≤ 1 SE;
else FAIL. Calibration = actual − predicted. No dev pass => virgin
NOT read.

The halves constant in FEATURES (goals 0.436) is a reporting
constant only; no candidate may fit a team-specific halves model.
