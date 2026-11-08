# Features — Brazil Série C

All features obey strict pre-match causality and use team IDs. Missing data stays NULL and deactivates an arm.

| feature | verdict | evidence |
|---|---|---|
| X1 blend | ADOPTED, goals-only in effect | xG is nowhere in payload stats; production fallback is goals-only |
| X2 mover offsets | ADOPTED | pooled ex-B dGF/dGA −0.0405/−0.0868 (n=346); newcomers −0.0627/+0.0667 (n=340) |
| X3 set-play xG | DROPPED | no xG values in 1,229 matches; set-play split does not exist |
| X4 xG/shot | DROPPED | no xG and shotmap shots=0 everywhere |
| X6 xGOT | DROPPED | no shotmap/xGOT in any season |
| X5 trailing form | ADOPTED as naive G baseline/harness component | score-based trailing form exists; SOT/corner/card/shot forms do not |
| X7 covariate | DROPPED | stats_nonnull=0 and stats_value_n=0 |
| X8 referee | DROPPED | referee text in only 15/1,286 payloads, all in 2025 |
| X9 covariates | DROPPED | no stats covariates exist |

Rejected list, adapted from J1: R1 team half shares (F3 true variance ≈0 and team split-half r=−0.37); R2 finishing; R3 conversion; R4 standalone on-target rate; R5 defensive xGOT; R6 lineup/absence (lineups exist only in 2025–2026 and the V10 absence finding remains closed); R7 top-shooter concentration; R8 formation/coach; R9 standings/H2H/form snapshots; R10 attendance; R11 first-goal/game-state; R12 red cards; R13 momentum. These are rejected for absent inputs, leakage, rare-event/noise concerns, or lack of a new reliability check. The half constant is presentation-only, not a feature.
