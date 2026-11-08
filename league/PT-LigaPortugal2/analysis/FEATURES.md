# Features and causality contract

For any target match, a feature may use only matches with kickoff strictly
before that target, within the same league unless explicitly identified as a
cross-tier mover input. Ratios are ratios of sums. Missing windows make an
arm inactive; they are never filled with target or future information. The
2025/2026 virgin and 2026/2027 confirmatory rows are not used to fit or tune
anything in this phase.

## X1–X9 decisions

| feature | decision | evidence / implementation boundary |
|---|---|---|
| X1 goals-only observation pair | **ADOPTED** | Goals exist for 1,619/1,619; xG is present 0/1,619 and shotmaps are empty. Goals model uses the documented 100% goals-only fallback. |
| X2 cross-tier mover offset | **DROPPED** | Counts are 3/3 per direction in 2022/23–2024/25, then 1/2 and 2/2; magnitudes change direction/size. No fixed offset is justified. |
| X3 set-play xG | **DROPPED** | No xG key anywhere. |
| X4 xG per shot | **DROPPED** | No xG and no non-empty shotmap. |
| X5 trailing target means | **DROPPED for buildability** | SOT/corners exist in only 396 matches across one partial and one full season; stats yellows exist in 0 matches. Too little multi-era dev history. |
| X6 attacking xGOT per shot | **DROPPED** | No shotmap/xGOT source. |
| X7 box touches | **DROPPED for buildability** | `touches_opp_box` is absent from the stats blocks; 0/396 stats matches. |
| X8 referee rate | **DROPPED** | Named referee coverage is 0/1,619 (0%). |
| X9 corners covariates | **DROPPED for buildability** | Corners are available in only 396 matches, all in the same short stats era; no season-blocked multi-era dev window exists. |

## Rejected analogues

First-half team shares are not model features: period-split stats are
0/1,619, so only the descriptive event-derived 1H goal share is retained.
Finishing, conversion, xG-derived quality, shotmap features, standings,
form snapshots, head-to-head, attendance, first-goal/game-state traits,
lineups/absences, formation/coach fields, red-card rates, and momentum are
rejected as unavailable, post-match/leaky, insufficiently reliable, or not
pre-match.

## Causality contract

The target payload contributes only static fixture facts (team IDs, venue,
and any independently available pre-match appointment). A fitted state may
never be trained on a match at or after the target kickoff. Expanding
season-blocked fits, signed-age decay, and unseen-team league-mean defaults
must preserve that rule. This document is the eligibility boundary for the
model-design phase; adding a feature requires new pre-registered reliability
evidence.
