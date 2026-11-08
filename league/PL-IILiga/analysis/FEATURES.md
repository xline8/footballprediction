# Phase 4 — Features

X1 is ADOPTED: the production 0.5 goals / 0.5 xG blend pattern remains,
but xG exists in zero payloads, so the fallback fires everywhere and
Gate Zero is goals-only DC. X2 is MEASURED, NOT CONSUMED: dev movers are
I-Liga-relegated n=9, GF −0.057 / GA −0.060, and from-below n=12,
GF +0.113 / GA −0.023 (all-complete: relegated n=11, −0.017/−0.100;
from-below n=17, +0.137/−0.041). The gaps are tiny and the from-below
sign is opposite to a promotion penalty, so no offset is estimated or
consumed. X3 set-play xG share/rate is DROPPED: the stats feed carrying
`expected_goals_set_play` exists in 0/1,679 payloads. X4 shotmap xG per
shot is DROPPED: the shotmap is empty in 1,679/1,679 payloads. X5
trailing target-rate means is DROPPED for every target: no SOT, corners,
or yellow-card target exists in any payload (the event feed carries goals
plus 365 dismissal-only Card events — 173 Red, 192 YellowRed, zero
plain-Yellow — with no stats feed to unify against). X6 attacking xGOT
per shot is DROPPED: `expectedGoalsOnTarget` exists in 0/1,679 payloads.
X7 opp-box touches is DROPPED: `touches_opp_box` exists in 0/1,679
payloads. X8 referee yellow rate is DROPPED: no referee is named in any
payload. X9 possession / big chances is DROPPED as a covariate: the
stats feed carrying `BallPossesion` / `big_chance` exists in 0/1,679
payloads (it remains the production reference pattern only in the sense
that Gate Zero copies the DC fit, not the corners covariates — there is
no corners candidate here at all).

R1 halves is noise (the 0.4270 constant is presentation-only). R2
finishing, R3 conversion, R4 on-target rate, R5 xGOT, R7 concentration,
and R8 formation/coach have no admissible payload evidence. R6 lineup /
absence is closed: `content.lineup` is null in 1,678/1,679 payloads and
the single non-null block (match 5862683, Znicz Pruszków vs GKS Tychy,
2026-09-11) is `lineupType: 'unavailable'` with empty starters — there
is effectively no lineup data in 1,679/1,679 rows. R9 standings/h2h/table snapshots
are post-match leakage. R10 attendance is not pre-match; R11 game state
is in-match; R12 reds are sparse with no reliability evidence; R13
momentum is in-match. No feature not listed here may enter the fit.
