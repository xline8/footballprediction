# Step 3.5 — Features: AU-Championship (J1 template X1–X9)

Every J1 template feature is **DROPPED**. The reasons split two
ways: for the goals candidate the sample cannot support a trailing
feature at all (one complete season, 6–9 matches per team); for the
other four candidates the underlying data does not exist in any
payload.

| # | J1 feature | Verdict | Reason (this league) |
|---|-----------|---------|----------------------|
| X1 | Blend observation pair (goals-model training input: 0.5·goals + 0.5·xG) | **DROPPED** | No xG in any payload (stats null 87/87, shotmap empty 87/87). The blend collapses to goals-only by construction, and there is no dev window in which a goals-only DC fit could be validated anyway (MODEL_DESIGN.md). |
| X2 | Mover tier offset (prior for promoted/relegated clubs) | **DROPPED** | No mover prior exists. A-League overlap is zero (13 senior clubs vs 20 Championship clubs, disjoint), so the sibling cannot supply one. Same-club state-league form is not a mover offset: it is same-season concurrent form (state Feb–Sep → Championship Oct–Dec), 48% of state scores are unrecorded, and there is no in-competition dev/virgin window against which any offset could be validated. |
| X3 | Set-play xG share and rate (trailing) | **DROPPED** | No xG, no shotmap, no events. A set-play rate cannot be computed. |
| X4 | xG per shot (trailing) | **DROPPED** | No xG, no shots. Undefined. |
| X5 | Trailing target-rate means (naive / ensemble components) | **DROPPED** | No trailing means exist for any target. For goals: teams play 6–9 matches per season and the competition has one complete season — a "trailing" rate would be 0–6 matches of history, and the reliability check cannot run (EDA F4). For SOT/corners/cards/total shots the target itself is absent. |
| X6 | Attacking xGOT per shot (trailing, era-guarded) | **DROPPED** | xGOT is not in the payloads at all. |
| X7 | Opp-box touches for/against (trailing) | **DROPPED** | `touches_opp_box` does not exist (no stats block in any payload). |
| X8 | Referee yellow rate (trailing) | **DROPPED** | No referee field in any of the 1,333 parent payloads (blank 1,333/1,333). The referee arm is unavailable in principle, not just in sample. |
| X9 | Reference territorial covariates (corners Gate Zero arm) | **DROPPED** | The corners Gate Zero multiplier needs fitted territorial covariates from a dev window; there is no dev window, and the corners target itself is absent. |

## Halves constants

None frozen. There are zero period-split observations in this league
(stats null 87/87), so 1H shares cannot be measured for any market.
Every market would be FT-only — and no market is built.

## Consumption map

No candidate consumes any feature. G-AUCH / S-AUCH / C-AUCH /
K-AUCH / T-AUCH are all NOT BUILDABLE (see MODEL_DESIGN.md and the
prereg).
