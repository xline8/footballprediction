# Features (AZ X1–X9 map)

Only G-AZ is buildable. The consumption rule is strict: a later design may
use only accepted features and the architectural components explicitly named.

| Feature | Decision | Reason |
|---|---|---|
| X1 goals observation pair | ADOPTED (goals-only) | Official FT goals exist in all 914; no xG feed exists. |
| X2 mover tier offset | DROPPED | No sibling Azerbaijani league and no prior tier source; entrants are descriptive only. |
| X3 set-play xG | DROPPED | No xG or set-play observations. |
| X4 xG/shot | DROPPED | Shotmap shots are empty in 914/914. |
| X5 trailing target rates | DROPPED as feature | No target stats; the DC home parameter remains fitted. |
| X6 xGOT | DROPPED | No xGOT. |
| X7 box touches | DROPPED | No territorial stats. |
| X8 referee rate | DROPPED | Named referee coverage is 0/914. |
| X9 territorial covariates | DROPPED | No possession or big-chance stats. |

## Halves constants

Frozen, presentation-only goals 1H share: **0.4344** (725/1669 dev goals,
605 matches). SOT, corners, total shots, and yellow cards are null.

## Rejected features

| # | Feature | Verdict / reason |
|---|---|---|
| R1 | Team first-half shares | **NOISE** — EDA variance is below binomial noise; no stable team signal. |
| R2 | Finishing (goals − xG) | **REJECTED** — xG absent. |
| R3 | Conversion (goals / shot) | **REJECTED** — shots absent and outcome-contaminated. |
| R4 | Standalone SOT/shots | **REJECTED** — SOT and shots absent. |
| R5 | Defensive xGOT/shot | **REJECTED** — xGOT absent. |
| R6 | Lineup/absence features | **CLOSED** — lineups and playerStats are absent throughout. |
| R7 | Top-shooter concentration | **NO EVIDENCE** — no playerStats. |
| R8 | Formation/coach | **NO EVIDENCE** — no lineups. |
| R9 | Standings, h2h, form snapshots | **LEAKAGE** — post-match payload state. |
| R10 | Attendance | **NOT PRE-MATCH** — actual crowd is post-match. |
| R11 | First goal/game state | **NOT PRE-MATCH** — in-match facts. |
| R12 | Red-card rates | **REJECTED** — 154 rare Red/YellowRed events and no reliability basis. |
| R13 | Momentum or virgin-derived features | **NOT PRE-MATCH / RESERVED** — no live feature; virgin seasons remain closed. |
