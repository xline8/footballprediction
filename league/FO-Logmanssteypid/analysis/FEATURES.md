# Step 3.5 — Features: FO-Logmanssteypid (J1 template X1–X9)

Every J1 template feature is **DROPPED**. The reason is the same in
every case and is structural, not a data gap that more collection
would fix: the competition plays 1 match a year between 2 teams that
never meet again in it. No trailing team statistic exists inside this
competition, so no feature can be computed, let alone pass a
reliability check. Features borrowed from the Faroese Premier League
would be Premier League features, not Løgmanssteypið features, and
could not be validated against any in-competition dev or virgin
window (see MODEL_DESIGN).

| # | J1 feature | Verdict | Reason (this league) |
|---|-----------|---------|----------------------|
| X1 | Blend observation pair (goals-model training input) | **DROPPED** | No training input exists: 6 matches total, 1/season; a DC fit would have 6 teams × 2 ratings on 6 observations, and each season's teams have zero prior in-competition matches. |
| X2 | Mover tier offset (prior for promoted/relegated clubs) | **DROPPED** | No movers: the two finalists each year are cup finalists, not promoted clubs; and there is no Faroese sibling league in this build to borrow a mover prior from (the Premier League, id 250, is a separate league — see MODEL_DESIGN). No dev window exists to estimate any prior. |
| X3 | Set-play xG share and rate (trailing) | **DROPPED** | No xG anywhere: shotmap is empty in 6/6 payloads; a trailing rate over 1 match/year is undefined. |
| X4 | xG per shot (trailing) | **DROPPED** | Same as X3: no shots, no xG, in any payload. |
| X5 | Trailing target-rate means (naive / ensemble components) | **DROPPED** | No trailing means exist for any target: SOT/corners/total shots/cards have 0 observations in 6 years; goals have 6 observations, one per team-season, so no team has a rate history. |
| X6 | Attacking xGOT per shot (trailing, era-guarded) | **DROPPED** | xGOT is not in the payloads at all (no shot-level data of any kind). |
| X7 | Opp-box touches for/against (trailing) | **DROPPED** | `touches_opp_box` exists in 0/6 payloads (no stats block at all); a trailing team rate over 1 match/year is undefined, and the reliability check cannot run (no repeated team-seasons). |
| X8 | Referee yellow rate (trailing) | **DROPPED** | No referee field in any of the 6 payloads (0/6), and no card data of any kind (events feed empty). The referee arm is unavailable in principle, not just in sample. |
| X9 | Reference territorial covariates (corners Gate Zero arm) | **DROPPED** | The corners Gate Zero multiplier needs fitted territorial covariates from a dev window; there is no dev window, and no corners data at all (0/6). |

## Halves constants

None frozen. No 1H share exists for any market (no stats splits, no
goal-minute events), so there is not even a descriptive share to
report — see EDA.md.

## Consumption map

No candidate consumes any feature. G-FOL / S-FOL / C-FOL / K-FOL /
T-FOL are all NOT BUILDABLE (see MODEL_DESIGN.md and the prereg).
