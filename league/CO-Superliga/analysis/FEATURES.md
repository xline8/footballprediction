# Step 3.5 — Features: CO-Superliga (J1 template X1–X9)

Every J1 template feature is **DROPPED**. The reason is the same in
every case and is structural, not a data gap that more collection would
fix: the competition plays 2 matches a year between 2 teams that never
meet again in it. No trailing team statistic exists inside this
competition, so no feature can be computed, let alone pass a reliability
check. Features borrowed from the parent league (Primera A) would be
Primera A features, not Superliga features, and could not be validated
against any in-competition dev or virgin window (see MODEL_DESIGN).

| # | J1 feature | Verdict | Reason (this league) |
|---|-----------|---------|----------------------|
| X1 | Blend observation pair (goals-model training input) | **DROPPED** | No training input exists: 12 matches total, 2/season; a DC fit would have 9 teams × 2 ratings on 12 observations, and each season's teams have zero prior in-competition matches. |
| X2 | Mover tier offset (prior for promoted/relegated clubs) | **DROPPED** | No movers: the two entrants each year are the Primera A champions, not promoted clubs; and a cross-tier prior needs a dev window to estimate, which does not exist. (Note: Primera A itself adopted an X2 arm from Primera B; that is a Primera A feature, not transferable here — see MODEL_DESIGN.) |
| X3 | Set-play xG share and rate (trailing) | **DROPPED** | No trailing window: xG exists in 4/12 payloads (2025–26 only); a trailing rate over 2 matches/year is undefined. |
| X4 | xG per shot (trailing) | **DROPPED** | Same as X3: xG in 4 matches, shotmap empty before 2025. |
| X5 | Trailing target-rate means (naive / ensemble components) | **DROPPED** | No trailing means exist for any target: SOT/corners/total shots have 7 observations in 6 years; cards have 12 event counts but no team has a rate history. |
| X6 | Attacking xGOT per shot (trailing, era-guarded) | **DROPPED** | xGOT is not in the payloads at all (no `expected_goals_on_target` shot-level field before 2025; the stats-block xGOT appears only in 2025–26, 4 matches). |
| X7 | Opp-box touches for/against (trailing) | **DROPPED** | `touches_opp_box` exists only in the 7 stats matches; a trailing team rate over 1–2 matches/year is undefined, and the reliability check cannot run (no repeated team-seasons). |
| X8 | Referee yellow rate (trailing) | **DROPPED** | No referee field in any of the 12 payloads (0/12). The referee arm is unavailable in principle, not just in sample. |
| X9 | Reference territorial covariates (corners Gate Zero arm) | **DROPPED** | The corners Gate Zero multiplier needs fitted territorial covariates from a dev window; there is no dev window. |

## Halves constants

None frozen. 1H shares (goals 0.345 on 29 goals; total shots 0.421,
corners 0.464, SOT 0.386 on 7 matches) are descriptive noise at these n
(see EDA.md) and are not adopted as presentation constants.

## Consumption map

No candidate consumes any feature. G-COS / S-COS / C-COS / K-COS / T-COS
are all NOT BUILDABLE (see MODEL_DESIGN.md and the prereg).
