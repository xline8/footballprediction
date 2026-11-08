# Features

The feature contract is causal: only matches strictly before a target kickoff may contribute. The EDA scope is seasons 2021–2025; 2026 is virgin-only.

| Feature | Decision | Reason |
|---|---|---|
| X1 goals observation pair | ADOPTED | Goals exist for every group row; goals-only Dixon–Coles input. |
| X2 newcomer prior | ADOPTED conditionally | F4 mover blocks are measurable; pooled FEDA-vs-season team-match gaps are retained as preregistration inputs, not constants fitted after the fact. |
| X3 set-play xG | DROPPED | xG/stats absent in 0/3,219 payloads. |
| X4 xG per shot | DROPPED | shotmap and xG absent in 0/3,219. |
| X5 trailing target means | ADOPTED for goals | Trailing goals-for/goals-against means are available; no SOT/corners/Yellow target exists. |
| X6 xGOT | DROPPED | No shotmap/xGOT. |
| X7 box-touch territory | DROPPED | Stats block absent. |
| X8 referee rate | DROPPED | Referee coverage is 0/3,219. |
| X9 territorial covariates | DROPPED | Possession/big-chance stats absent. |

The goals halves constant is ADOPTED for presentation only. Across the EDA window, the 1H goal share (ratio of sums) is 0.463826; observed variance 0.13718731 is below the estimated noise floor 0.13896050, so the frozen-constant test passes. No team-specific halves feature is adopted.

Rejected list: R1 team first-half traits (frozen-constant result, not a team signal); R2 finishing (no xG); R3 conversion (no shots); R4 SOT/shots (no targets); R5 defensive xGOT (absent); R6 lineups/absence (not a Phase-A measured feature); R7 top-shooter concentration (not tested); R8 formation/coach (not tested); R9 standings/form snapshots (leakage); R10 attendance (post-match); R11 first-goal/game-state traits (not pre-match); R12 red-card traits (rare and no Yellow target); R13 momentum (in-match).
