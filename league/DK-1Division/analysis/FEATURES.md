# Feature decisions — DK-1Division

The causality contract is strict: only pre-match observations, trailing or expanding-with-decay windows, ratio-of-sums, NaN means an inactive arm, and no target-row leakage.

| Feature | Verdict | Evidence in this league |
|---|---|---|
| X1 goals + xG observation blend | **DROPPED** | expected_goals absent in all 1,043 JSONs |
| X2 mover tier offset | **ADOPTED** | 10 mover team-seasons and 300 prior Superliga matches in each direction; feasible but estimated only in Phase B |
| X3 set-play xG share | **DROPPED** | xG and set-play xG absent |
| X4 xG per shot | **DROPPED** | shotmap and xG absent |
| X5 trailing target-rate means | **ADOPTED** | SOT r=.694, corners r=.822, shots r=.755; cards target available 2022/2023+ |
| X6 xGOT/shot | **DROPPED** | shotmap absent |
| X7 opp-box touches | **ADOPTED** | r=.583; all-period coverage begins 2022/2023 |
| X8 referee yellow rate | **DROPPED** | strictness r=.305; coverage also varies 75.0–97.9% |
| X9 possession/big-chance reference covariates | **DROPPED** | not eligible as a stable reference feature without a measured production analogue in this feed |

Team half shares are rejected as features; only the frozen league constants in `config.yaml` may be used for presentation. Reds are not a candidate target. Standings, h2h, attendance, lineups, formations, and game-state events are post-match or otherwise not pre-match-safe.
