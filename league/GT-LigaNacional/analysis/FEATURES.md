# Features and causality contract

Features may use only strictly earlier matches in the same league unless an
explicit cross-tier feature is authorized. This phase performs no fitting and
does not tune on virgin or confirmatory seasons.

| feature | decision | Guatemala evidence / boundary |
|---|---|---|
| X1 goals/xG observation pair | **ADOPTED: goals-only** | Header goals exist in 1,443/1,443 matches; xG shots exist in 0. |
| X2 mover tier offset | **DROPPED** | Guatemala has no other warehouse league; no sibling-tier mover evidence exists. |
| X3 set-play xG | **DROPPED** | No xG or stats block exists. |
| X4 xG per shot | **DROPPED** | Shotmaps have zero shots and zero xG shots. |
| X5 trailing target means | **DROPPED** | SOT, corners, total shots, and stats yellows have zero observations; event cards are dismissals only and unvalidated. |
| X6 attacking xGOT per shot | **DROPPED** | No shotmap shots or xGOT source. |
| X7 opponent-box touches | **DROPPED** | `content.stats` is `None` in 1,443/1,443 matches. |
| X8 referee yellow rate | **DROPPED** | Named referee coverage is 0/1,443. |
| X9 territorial corners covariates | **DROPPED** | No stats block and no corners observations. |

First-half shares are descriptive only. Lineups, standings, attendance,
in-match state, and event cards are not eligible pre-match features in this
phase. Adding a feature requires new reliability evidence.
