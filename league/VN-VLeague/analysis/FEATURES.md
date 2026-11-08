# Features (J1 X1–X9 map)

Consumption map: G-VN only (goals). S/C/K/T are not buildable — see
MODEL_DESIGN and `prereg/PREREG_NOT_BUILDABLE_SCKT_VN.md`.

| Feature | Decision | Reason |
|---|---|---|
| X1 blend / goals-only fallback | ADOPTED (goals-only) | No xG/stats feed in any season; DC observes goals only. |
| X2 mover offset | DROPPED | No Vietnamese sibling league in the warehouse — no mover prior. Entrant deviations are measured descriptively in EDA F4 (3 real entrants, mean GF diff +0.18, GA diff −0.02 — no systematic weakness) but no arm is registered. |
| X3 set-play | DROPPED | No xG/set-play observations. |
| X4 xG/shot | DROPPED | No xG or shots. |
| X5 trailing target-rate means | DROPPED as feature; home advantage ADOPTED as fitted DC parameter | Goals-only DC retains the production home parameter; trailing rates are not an extra covariate. The naive trailing-10 remains a harness baseline. |
| X6 xGOT | DROPPED | No xGOT. |
| X7 box touches | DROPPED | No territorial stats. |
| X8 referee | DROPPED | Named referee coverage is 0/969 — the infoBox Referee text is the empty string in every payload. |
| X9 territorial covariates | DROPPED | No possession/territorial stats. |

## Halves constants (frozen, presentation-only)

- Goals 1H share: **0.4468** (dev 2021–2024/2025, 1,831 goals, 695 matches; EDA F3). SOT / corners / total shots / cards: none (no splits exist).

## Rejected features (explicit)

| # | Feature | Verdict / reason |
|---|---|---|
| R1 | half-share modelling | **REJECTED** — F3: per-match 1H share variance 0.1320 vs binomial-noise expectation 0.1243 (excess 0.0077); team split-half r = 0.24 (n = 17). Frozen goals constant 0.4468 is presentation-only. |
| R2 | finishing / conversion | **REJECTED** — no shots/xG in any season. |
| R3 | lineup / absence | **REJECTED** — lineups exist only from 2024/2025 (413/969 matches, no playerStats ever); no EDA-grade reliability check was run; closed by program precedent (V10 star-absence test failed; J1 FEATURES R6). |
| R4 | post-match snapshots / standings | **REJECTED** — leakage by construction (`content.table`/`h2h` are post-match snapshots). |
| R5 | head-to-head snapshots | **REJECTED** — sparse / leakage. |
| R6 | reds as target | **REJECTED** — 46–52 Red+YellowRed events per pre-2024/2025 season, a rare-event count with no reliability evidence; the production cards design excludes reds as a target. |
| R7 | plain-yellow target | **REJECTED** — zero plain-Yellow events in 2021–2023/2024 (0/556 matches); the feed switches on only in 2024/2025, so no dev season contains the target. |
| R8 | referee strictness | **REJECTED** — zero named-referee coverage (0/969). |
| R9 | shots / SOT / corners | **REJECTED** — targets absent in every season (stats Periods empty, shotmap empty). |
| R10 | xG / xGOT | **REJECTED** — absent in every season. |
| R11 | possession / box touches | **REJECTED** — absent in every season. |
| R12 | split-group phase effects | **REJECTED** — the 2023 phase-2 groups are 43 matches inside one dev season; too thin to fit a phase effect, and the DC ratings already absorb team strength across phases. Phase is recorded in the CSV, not modelled. |
| R13 | 2025/2026- or 2026/2027-derived features | **REJECTED** — virgin season reserved; in-progress season reserved for the season-end confirmatory read. |
