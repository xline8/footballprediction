# Features (J1 X1–X9 map)

Consumption map: G-KZ only.

| Feature | Decision | Reason |
|---|---|---|
| X1 blend / goals-only fallback | ADOPTED | No xG/stats feed; DC observes goals only. |
| X2 mover offset | DROPPED | No Kazakh sibling league exists in the warehouse — no mover prior (brief). Entrant deviations are measured descriptively in EDA F4 (mean GF −0.22, GA +0.16, n=6) but no arm is registered. |
| X3 set-play | DROPPED | No xG/set-play observations. |
| X4 xG/shot | DROPPED | No xG or shots. |
| X5 trailing target-rate means | DROPPED as feature; home advantage ADOPTED as fitted DC parameter | Goals-only DC retains the production home parameter; trailing rates are not an extra covariate. The naive trailing-10 remains a harness baseline. |
| X6 xGOT | DROPPED | No xGOT. |
| X7 box touches | DROPPED | No territorial stats. |
| X8 referee | DROPPED | Named referee coverage recomputes to 0/1,124. |
| X9 territorial covariates | DROPPED | No possession/territorial stats. |

| R1 | half-share modelling | **REJECTED** — F3: team 1H share is noise (career split-half r=0.086, n=20; within team-season r=−0.239, n=69; season-demeaned r=0.077, n=20); frozen goals constant 0.4539 is presentation-only |
| R2 | finishing / conversion | **REJECTED** — no shots/xG in any season |
| R3 | lineup / absence | **REJECTED** — zero starter lineups in any season (81 payloads carry only unavailable/injury lists) |
| R4 | post-match snapshots / standings | **REJECTED** — leakage by construction |
| R5 | head-to-head snapshots | **REJECTED** — sparse / leakage |
| R6 | reds as target | **REJECTED** — 127 dev Red + 68 YellowRed events, no consistent card target |
| R7 | plain-yellow target | **REJECTED** — zero plain Yellow events in any season |
| R8 | referee strictness | **REJECTED** — zero named-referee coverage (0/1,124) |
| R9 | shots / SOT / corners | **REJECTED** — targets absent in every season |
| R10 | xG / xGOT | **REJECTED** — absent in every season |
| R11 | possession / box touches | **REJECTED** — absent in every season |
| R12 | phase-specific effects | **REJECTED** — single round-robin table; no split group or playoff phase exists to model |
| R13 | 2026-derived features | **REJECTED** — virgin season reserved |
