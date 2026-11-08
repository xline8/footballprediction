# Features — NZ-Championship

| Template feature | Decision | Reason |
|---|---|---|
| X1 | ADOPTED | Goals-only fallback; no xG exists anywhere. |
| X2 | DROPPED | No sibling league in the warehouse (only Championship 8870 exists for New Zealand), so no mover prior can be estimated; F4 entrant deviations are descriptive only and mostly returnees. |
| X3 | DROPPED | No xG splits. |
| X4 | DROPPED | No shotmap or xG (shotmap payloads are present but empty on 221/221). |
| X5 | NOT APPLICABLE standalone | The goals ratings are the team-trait mechanism (F2, weak: GF r=0.2293, GA r=0.2570). SOT, corners, cards and shots trailing target-rate means do not exist. |
| X6 | DROPPED | No shotmap/xGOT. |
| X7 | DROPPED | No stats, hence no box touches. |
| X8 | DROPPED | No referee names, 0/221. |
| X9 | DROPPED | No stats, hence no possession/big chances. |

The frozen goals first-half share is 0.4123 and is presentation-only.
Rejected: half-share modelling (F3: observed per-match share variance
0.084888 is below the binomial noise floor 0.086947; team split-half
r=0.0159), finishing/form, lineup/absence features, standings or H2H
snapshots, and reds as a target. These are not introduced after seeing
dev results.
