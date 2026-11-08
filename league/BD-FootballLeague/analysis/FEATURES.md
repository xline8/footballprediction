# Features (BD X1–X9 map)

Only G-BD is buildable. The consumption rule is strict: a later design may
use only accepted features and the architectural components explicitly named.

| Feature | Decision | Reason |
|---|---|---|
| X1 goals observation pair | ADOPTED (goals-only) | Official FT goals exist in all 394; no xG feed exists. |
| X2 mover tier offset | DROPPED | No sibling Bangladeshi league and no prior tier source; entrants are descriptive only (F4: mean GF −0.49 / GA +0.93 over five real entrants). |
| X3 set-play xG | DROPPED | No xG or set-play observations. |
| X4 xG/shot | DROPPED | Shotmap shots are empty in 394/394. |
| X5 trailing target rates | DROPPED as feature | No target stats; the DC home parameter remains fitted. The trailing-10 naive baseline in the harness is an evaluation baseline, not a model feature. |
| X6 xGOT | DROPPED | No xGOT. |
| X7 box touches | DROPPED | No territorial stats. |
| X8 referee rate | DROPPED | Named referee coverage is 33/394 and 0/365 in dev; no referee history exists to trail. |
| X9 territorial covariates | DROPPED | No possession or big-chance stats. |

## Halves constants

Frozen, presentation-only goals 1H share: **0.4217** (447/1060 dev goals,
365 matches). SOT, corners, total shots, and yellow cards are null.

## Rejected features

| # | Feature | Verdict / reason |
|---|---|---|
| R1 | Team first-half shares | **NOISE** — EDA F3: excess variance −0.0017; team split-half r=0.207 on n=16 teams does not clear any reliability bar. |
| R2 | Finishing (goals − xG) | **REJECTED** — xG absent. |
| R3 | Conversion (goals / shot) | **REJECTED** — shots absent and outcome-contaminated. |
| R4 | Standalone SOT/shots | **REJECTED** — SOT and shots absent. |
| R5 | Defensive xGOT/shot | **REJECTED** — xGOT absent. |
| R6 | Lineup/absence features | **CLOSED** — lineups exist but no reliability check was run and no absence signal was measured; the top-5 V10 closure stands. |
| R7 | Top-shooter concentration | **NO EVIDENCE** — no playerStats. |
| R8 | Formation/coach | **NO EVIDENCE** — no reliability check run. |
| R9 | Standings, h2h, form snapshots | **LEAKAGE** — post-match payload state. |
| R10 | Attendance | **NOT PRE-MATCH** — actual crowd is post-match. |
| R11 | First goal/game state | **NOT PRE-MATCH** — in-match facts. |
| R12 | Red-card rates | **REJECTED** — 59 rare Red/YellowRed events and no reliability basis. |
| R13 | Momentum or virgin-derived features | **NOT PRE-MATCH / RESERVED** — no live feature; the virgin season remains closed until its one read. |
