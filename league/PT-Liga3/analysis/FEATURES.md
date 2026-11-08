# Features and causality contract

Features may use only strictly earlier matches in the same league unless
explicitly cross-tier. This phase performs no fitting and does not tune on
the virgin or confirmatory seasons.

| feature | decision | Liga 3 evidence / boundary |
|---|---|---|
| X1 goals/xG observation pair | **ADOPTED: goals-only** | Goals exist in 1,647/1,647 finished matches; xG keys and non-empty shotmaps exist in 0. |
| X2 mover tier offset | **DROPPED** | Direct PT↔PT3 movers are 0; PT2↔PT3 is only 1–3 per direction/transition. |
| X3 set-play xG | **DROPPED** | No xG or stats block exists. |
| X4 xG per shot | **DROPPED** | 0 non-empty shotmaps and 0 xG shots. |
| X5 trailing target means | **DROPPED** | SOT, corners, total shots, and stats yellows have 0 observations; event yellows are unstable and unvalidated. |
| X6 attacking xGOT per shot | **DROPPED** | No shotmap shots or xGOT source. |
| X7 opponent-box touches | **DROPPED** | `content.stats` is None in 1,647/1,647 matches. |
| X8 referee yellow rate | **DROPPED** | Named referee coverage is 0/1,647. |
| X9 territorial corners covariates | **DROPPED** | No stats block and no corners observations. |

First-half shares remain descriptive only. Lineups, standings, snapshots,
attendance, in-match state, and event cards are not eligible pre-match model
features in this phase. Adding a feature requires new reliability evidence.
