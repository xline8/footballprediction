# Features (J1 X1–X9 map)

Consumption map: G-UYSEG only.

| Feature | Decision | Reason |
|---|---|---|
| X1 blend / goals-only fallback | ADOPTED | No xG/stats feed; DC observes goals only. |
| X2 mover offset | ADOPTED as gated arm | 12 relegated entrants are measurable; offsets are frozen cumulatively from dev transitions. |
| X3 set-play | DROPPED | No xG/set-play observations. |
| X4 xG/shot | DROPPED | No xG or shots. |
| X5 trailing target-rate means | DROPPED as feature; home advantage ADOPTED as fitted DC parameter | Goals-only DC retains the production home parameter; trailing rates are not an extra covariate. |
| X6 xGOT | DROPPED | No xGOT. |
| X7 box touches | DROPPED | No territorial stats. |
| X8 referee | DROPPED | Named referee coverage recomputes to 0/1,219. |
| X9 territorial covariates | DROPPED | No possession/territorial stats. |

| R1 | half-share modelling | **REJECTED** — F3: team 1H share is noise (within-team-season split-half r=0.146, n=54; season-demeaned r=0.265, n=26; per-match variance 0.1329 ≈ binomial noise floor); frozen goals constant is presentation-only |
| R2 | finishing / conversion | **REJECTED** — no shots/xG in any season |
| R3 | lineup / absence | **REJECTED** — zero lineups in any season |
| R4 | post-match snapshots / standings | **REJECTED** — leakage by construction |
| R5 | head-to-head snapshots | **REJECTED** — sparse / leakage |
| R6 | reds as target | **REJECTED** — 318 dev Red + 60 YellowRed events, no consistent card target |
| R7 | plain-yellow target | **REJECTED** — zero plain Yellow events in any season |
| R8 | referee strictness | **REJECTED** — zero named-referee coverage (0/1,219) |
| R9 | shots / SOT / corners | **REJECTED** — targets absent in every season |
| R10 | xG / xGOT | **REJECTED** — absent in every season |
| R11 | possession / box touches | **REJECTED** — absent in every season |
| R12 | phase-specific effects | **REJECTED** — phases not consistently labelled in payloads |
| R13 | 2026-derived features | **REJECTED** — transitional season reserved |
