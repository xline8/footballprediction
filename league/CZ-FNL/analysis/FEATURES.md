# Features — CZ-FNL

The global causality contract is strict: trailing state uses only matches
before kickoff; missing features remain missing. The only adopted feature is
the goals-only form of trailing goals means, and the pre-registered mover
offset below.

| Feature | Verdict | Reason |
|---|---|---|
| X1 xG blend pair | DROPPED | xG is absent in all 1,311 payloads. |
| X2 relegated-mover offset | ADOPTED | Four transitions are measurable; frozen offsets are in EDA and cumulative offsets are frozen before each target season. |
| X3 set-play xG | DROPPED | No xG or xG splits. |
| X4 xG per shot | DROPPED | Shotmap is empty in every match. |
| X5 trailing target means | ADOPTED, goals-only | Goals are the only target available for a trailing goals mean in this build. |
| X6 xGOT per shot | DROPPED | No shotmap/xGOT. |
| X7 opponent-box touches | DROPPED | No touches data; corners target C is not buildable. |
| X8 referee yellow rate | DROPPED | No named referees in the dev era; K is not buildable. |
| X9 possession/corners covariates | DROPPED | No possession data and C is not buildable. |

The frozen presentation constant is goals 1H share `0.449598` (1,173/2,609).
SOT, corners, total shots, cards, and their half constants are null.
