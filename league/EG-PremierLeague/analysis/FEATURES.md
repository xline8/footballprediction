# Phase 1 — Feature decisions: Egypt Premier League

All evidence is from eda_numbers.json. Consumption remains trailing/expanding and strictly pre-match; missing values deactivate an arm.

| Feature | Decision | Evidence |
|---|---|---|
| X1 goals + xG observation blend | **Adopted goals-only** | xG coverage is 0.0% through 2023/2024 and 0.4% in 2024/2025; it begins at virgin 2025/2026 |
| X2 parent-tier mover offset | **Dropped** | No parent tier exists in the warehouse |
| X3 set-play xG | **Dropped** | Virgin-only xG era, no dev validation |
| X4 xG/shot | **Dropped** | Virgin-only shotmap/xG era, no dev validation |
| X5 trailing target rates | **Adopted** | Dev reliability: SOT 0.774, corners 0.646, shots 0.856; yellows 0.262 |
| X6 xGOT/shot | **Dropped** | Shotmap begins at virgin; no dev validation |
| X7 box touches | **Adopted for corners** | touches-for r=0.791; coverage 39.2%, 68.6%, 93.8%, 98.7%, 100.0%, 100.0% |
| X8 referee yellows | **Dropped** (coordinator decision 2026-11-09, overriding the phase-1 draft) | r=0.290 on 32 dev referees is weak (TR adopted at r=0.505; SA dropped at r=−0.279) AND virgin-season referee coverage is only 26.7%, so an X8 arm would run mostly on its Gate Zero fallback in the virgin and could not ship honestly (cf. the DE-2Bundesliga X8 operational stop). K-EG is Gate Zero only. |
| X9 corner Gate Zero covariates | **Adopted** | Corners are available as a target in every season; Gate Zero is frozen |

Rejected: per-team half shares; finishing; standalone on-target rate; red-card target; phase feature; regime dummy; parent-tier mover offset. Half shares remain league constants only.
