# HU-NBI features and decisions

The global causality contract is inherited from the J1 template: only strictly pre-match observations, trailing or expanding-with-decay windows, ratios of sums, and NaN/inactive arms when a window cannot be filled. No feature below may be added after fitting.

| feature | decision | HU-NBI reason / reliability |
|---|---|---|
| X1 goals/xG observation blend | ADOPTED, goals-only | xG and shotmap absent; goals-only Dixon–Coles is the production fallback. |
| X2 cross-tier mover offset | DROPPED | No parent-tier corpus is in this phase; no HU-specific mover reliability can be estimated. |
| X3 set-play xG | DROPPED | xG keys absent. |
| X4 xG per shot | DROPPED | shotmap absent in all 1,067 rows. |
| X5 trailing target-rate means | ADOPTED | Candidate targets exist: event cards all rows and stats targets in 1,061 rows; split-half reliabilities are cards for .466/.377 (2022/23), .103/.340 (2023/24), .347/.417 (2024/25), and target-specific EDA values above. |
| X6 xGOT per shot | DROPPED | No shotmap/xGOT. |
| X7 opponent-box touches | DROPPED | Key absent in all seasons. |
| X8 referee yellow rate | DROPPED | Coverage is 18/198 in virgin 2025/26; split-half r is .343/.354/.470/.494 in earlier seasons but cannot meet virgin availability. |
| X9 territorial covariates | ADOPTED, possession-only | `BallPossesion` exists on 1,061 matches; box touches and big chances do not. The corners arm may use possession only. |

Architectural ratings, home advantage, Dixon–Coles rho, negative-binomial sizes, v5's internal ratio component, and the frozen half constants are not covariates. Red cards are rejected as a target: rare-event descriptive data only, not the program's yellow-card market.

Halves: goals 0.4471 and event-unified cards 0.3644 are frozen presentation constants. SOT, corners, and total shots are FT-only.

| candidate | base / adopted variants |
|---|---|
| G-HU-NBI | goals-only DC Gate Zero; optional pre-registered thin-team shrinkage arm |
| S-HU-NBI | `model_sot.py` v5 Gate Zero; optional ratio-shrink arm |
| C-HU-NBI | `model_corners_v3.py` possession-only Gate Zero; optional plain ablation |
| K-HU-NBI | `model_cards.py` event-unified Gate Zero; no referee variant |
| T-HU-NBI | J1 total-shots arm A Gate Zero; optional arms B/C only if justified by the reference design |
