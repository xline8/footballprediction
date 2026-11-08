# Features and causality contract

Features may use only strictly earlier matches in the same league
unless an explicit cross-tier feature is authorized. This phase
performs no fitting and does not tune on virgin or confirmatory
seasons.

| feature | decision | Honduras evidence / boundary |
|---|---|---|
| X1 goals/xG observation pair | **ADOPTED: goals-only** | Header goals exist in 1,132/1,132 matches; xG shots exist in 0. |
| X2 mover tier offset | **DROPPED** | Honduras has no other warehouse league; no sibling-tier mover evidence exists. |
| X3 set-play xG | **DROPPED** | No xG or stats block exists. |
| X4 xG per shot | **DROPPED** | Shotmaps have zero shots and zero xG shots. |
| X5 trailing target means | **DROPPED** | SOT, corners, total shots, and stats yellows have zero observations; event cards are dismissals only and unvalidated. |
| X6 attacking xGOT per shot | **DROPPED** | No shotmap shots or xGOT source. |
| X7 opponent-box touches | **DROPPED** | `content.stats` is `None` in 1,132/1,132 matches. |
| X8 referee yellow rate | **DROPPED** | Named referee coverage is 0/1,132. |
| X9 territorial corners covariates | **DROPPED** | No stats block and no corners observations. |

## Consumption contract

- **X1 (goals-only)** is the sole adopted feature. It enters the
  goals candidate as the Dixon-Coles observation (goals from the
  header score; no xG blend anywhere — the blend fallback applies
  to 100% of observations).
- **Team goal traits** (EDA §2: goals-for r = 0.839, goals-against
  r = 0.320, split-half, n = 16) are architectural evidence for the
  DC ratings, not covariates: ratings, home advantage, Dixon-Coles
  rho and time decay are fitted parameters of the shared
  architecture, estimated inside the fit under the signed-age rule.
- **League half-share constant** (goals 1H share 0.4572, EDA §3)
  is a frozen constant for report-style splits. It is not a
  feature, carries no team dimension, and may not be "improved"
  into a per-team or per-match quantity.
- **League base rates / naive baselines** belong to the evaluation
  harness, not to any model.

## Rejected (J1 §3 items that apply here)

| # | Feature | Verdict / reason |
|---|---|---|
| R1 | Team first-half shares (goals) | **NOISE** — EDA §3: true variance ≈ 0 (excess 0.0002); the frozen league constant is the only halves object. |
| R2/R3 | Trailing finishing / conversion | **NO EVIDENCE** — no xG or shot data exists to define them. |
| R4 | Trailing on-target rate | **NO EVIDENCE** — no SOT or shot data exists. |
| R6 | Lineup / absence features | **CLOSED** — no lineups exist in this corpus (0/1,132), and the V10 protocol result stands regardless. |
| R8 | Formation / coach features | **NO EVIDENCE** — no lineup data; no reliability check run. |
| R9 | Standings position, h2h, teamForm snapshots | **LEAKAGE** — `content.table`/`h2h` are post-match snapshots of the target match itself. |
| R10 | Attendance | **LEAKAGE / NOT PRE-MATCH** — the payload's figure is the actual crowd, known only after the match. |
| R11 | First-goal and other game-state traits | **NOT PRE-MATCH** — descriptive in-match facts only. |
| R12 | Red-card rates (as target or covariate) | **REJECTED** — 0.32 dismissals per match is a rare-event count with no reliability evidence; no yellow-card target exists to validate against. |
| R13 | Momentum | **NOT PRE-MATCH** — an in-match/live quantity in this payload. |

First-half shares are descriptive only, except for the frozen
goals constant above. Lineups, standings, attendance, in-match
state, and event cards are not eligible pre-match features in
this phase. Adding a feature requires new reliability evidence.
