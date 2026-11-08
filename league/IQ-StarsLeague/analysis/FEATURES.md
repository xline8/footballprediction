# Step 5 — Feature decision: IQ-StarsLeague

The causality contract is strict: a feature may use only earlier regular matches, and a missing payload field remains missing. In this scores-only league, only X1 is adopted.

| feature | decision | reason |
|---|---|---|
| X1 goals observation pair | ADOPTED | Final scores exist for every played CSV row; goals-only DC is feasible. xG is dropped because stats is null in 2,032/2,032. |
| X2 mover tier prior | DROPPED | No parent/sibling Iraq tier exists in the warehouse; no cross-league prior is estimated. |
| X3 set-play xG | DROPPED | No xG/stats keys anywhere. |
| X4 xG per shot | DROPPED | Shotmap shots are empty in 2,032/2,032. |
| X5 trailing target means | DROPPED for S/C/T/K | No valid SOT, corners, total-shots, or yellow-card target exists. Goals trailing means are DC observations, not a covariate. |
| X6 xGOT | DROPPED | No shotmap/xGOT data. |
| X7 territorial covariates | DROPPED | No stats keys. |
| X8 referee rate | DROPPED | Referee identity text is empty in 2,032/2,032. |
| X9 reference territorial covariates | DROPPED | No possession/big-chance stats. |

The only halves constant is goals: 0.4323308271, from 345 first-half goals / 798 event goals in event-verified regular 2024/2025 matches. SOT, corners, total shots, and yellows are null.

Rejected list: R1 per-team halves (EDA F3: per-match share SD 0.356 with no evidence beyond count noise); R9 standings/H2H snapshots (leakage); R10 attendance (post-match); R12 reds as a target (rare event, descriptive only); R13 live/game-state quantities (not pre-match). No lineup, formation, momentum, finishing, conversion, or cross-league mover feature is admitted without data and a fresh reliability test.

Consumption map: G-IQSL consumes X1 goals-only. S-IQSL, C-IQSL, T-IQSL, and K-IQSL consume nothing because they are not candidates.
