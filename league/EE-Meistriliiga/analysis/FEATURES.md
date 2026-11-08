# Features — G-EE

| feature | decision | reason |
|---|---|---|
| X1 goals observation | ADOPTED | Scores exist for 1,056/1,056; xG is absent in 1,056/1,056, so the blend is goals-only. |
| X2 mover offset | ADOPTED | Entrant deviations are directionally systematic in every pre-season window; frozen expanding offsets per target season (2023: dGF −0.358333 / dGA +1.030556; 2024: −0.440278 / +0.726389; 2025: −0.588889 / +0.716667; 2026 virgin: −0.498611 / +0.626389); X2 inactive for 2022 (no prior entrant). |
| X3 set-play xG | DROPPED | No stats or xG in any payload. |
| X4 xG/shot | DROPPED | No shotmap shots or xG in any payload. |
| X5 xGOT | DROPPED | No shotmap shots in any payload. |
| X6 box touches | DROPPED | No stats in any payload. |
| X7 SOT trailing mean | DROPPED | No stats in any payload. |
| X8 corner trailing mean | DROPPED | No stats in any payload. |
| X9 other shot/stat covariates | DROPPED | No stats or shotmap fields in any payload. |
| referee feature | DROPPED | No valid cards candidate; referee is not a goals input in the reference architecture. |

SOT, corners, total shots and cards are not buildable targets, so their
feature families are not reopened here.
