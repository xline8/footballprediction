# Step 3.5 — Features: Russia Second League (FotMob 9123)

Consumption rule (as J1): `MODEL_DESIGN.md` may use only the features
defined in §1 of this document, plus the architectural components
delimited in §2. Everything in §3 is rejected — explicitly, with its
reason — and may not re-enter through a later phase. The global
causality contract of J1 FEATURES.md applies verbatim (features from
matches strictly before kickoff; trailing windows or expanding-with-
decay inside a rating fit; ratios of sums; no silent filling).

## §1 Features

### X1 — Blend observation pair (goals-model training input)
- **ADOPTED as goals-only.** The observation is the pair
  (goals, team xG) in the production blend; here xG is absent from
  every one of the 6,558 payloads (`content.stats` empty), so the
  reference blend's documented fallback applies: matches enter
  goals-only. Goals from `header.status.scoreStr`, all seasons.
- The Dixon-Coles fit itself (ratings, home advantage, rho, time
  decay hl=270) is the §2 architectural component, unchanged.

### X2 — Mover tier offset (prior for promoted / relegated clubs)
- **DROPPED as a hard-coded offset; retained only as the motivation
  for the SHRINK arm.** Evidence (EDA.md §5): 9 relegated entrants
  from 1. Division (338) across the dev era, 0 from the Premier
  League (63); pooled first-season gaps GF −0.079 / GA −0.021 per
  match vs the pooled league mean — essentially zero, heterogeneous
  (Rotor +0.410 GF, Alania +0.726 GA), and group-confounded (entrants
  land in the Gold group). No offset is estimable from n=9, and
  G-RU1's prereg already settled that the sanctioned treatment is
  SHRINK, not a hard-coded offset. Mover identity is by FotMob team
  id (stable across leagues, verified).

### X3 — Set-play xG share and rate
- **DROPPED — data absent.** `expected_goals_set_play` exists in
  0/6,558 payloads. No reliability check is possible.

### X4 — xG per shot
- **DROPPED — data absent.** No shotmap in 0/6,558 payloads; no
  per-shot `expectedGoals` exists.

### X5 — Trailing target-rate means
- **DROPPED — targets absent.** SOT, corners and yellows exist in
  0/6,558 payloads (stats empty; events carry no SOT/corners and no
  plain Yellow events). There is no trailing mean to compute for any
  candidate. The goals model does not use a trailing-means component
  (its reference architecture is the DC fit, not the v5 ensemble).

### X6 — Attacking xGOT per shot
- **DROPPED — data absent.** No shotmap, no `expectedGoalsOnTarget`
  in any payload.

### X7 — Opp-box touches for / against
- **DROPPED — data absent.** `touches_opp_box` exists in 0/6,558
  payloads.

### X8 — Referee yellow rate
- **DROPPED — data absent.** Referee identity is empty in 6,558/6,558
  payloads and no yellow target exists to rate referees on.

### X9 — Reference territorial covariates (corners Gate Zero)
- **DROPPED — not applicable.** Corners is not a candidate here
  (no target); `BallPossesion` / `big_chance` exist in 0/6,558
  payloads in any case.

## §2 Architectural components — explicitly NOT features

- **Ratings, home advantage, Dixon-Coles rho, time decay** are fitted
  parameters of the shared architecture (justified by EDA §2: goals-
  for split-half r=.378, goals-against r=.500 pooled), not covariates.
- **League half-share constant (goals 0.4393)** is a frozen constant
  for report-style splits, per EDA §4 (true SD 0.0000). It is not a
  feature, carries no team dimension, and may not be "improved" into
  a per-team or per-match quantity.
- **League base rates / naive baselines** belong to the evaluation
  harness, not to any model.

## §3 REJECTED features (explicit; reason recorded for each)

| # | Feature | Verdict / reason |
|---|---|---|
| R1 | Team first-half shares (goals, SOT, corners, shots, xG) | **NOISE** — EDA §4: true variance 0.0000 for goals; other targets do not exist. Halves book stays closed. |
| R2 | Trailing finishing (goals − xG) | **NO EVIDENCE** — no xG exists; cannot be computed. |
| R3 | Trailing conversion (goals / shot) | **NO EVIDENCE** — no shot counts exist. |
| R4 | Standalone trailing on-target rate | **NO EVIDENCE** — no SOT/shots exist. |
| R5 | Defensive xGOT per shot | **NO EVIDENCE** — no shotmap exists. |
| R6 | Lineup / absence features | **CLOSED** — lineup shells only (25 payloads, id/name, no players); V10 protocol already closed this for SOT in production. |
| R7 | Top-shooter concentration share | **NO EVIDENCE** — never reliability-tested; no shot data exists. |
| R8 | Formation / coach features | **NO EVIDENCE** — no lineup/player data exists. |
| R9 | Standings position, h2h, teamForm snapshots | **LEAKAGE** — `content.table`/`h2h` are post-match snapshots of the target match itself. |
| R10 | Attendance | **LEAKAGE / NOT PRE-MATCH** — payload figure is the actual crowd. |
| R11 | First-goal and other game-state traits | **NOT PRE-MATCH** — in-match facts only. |
| R12 | Red-card rates (as target or covariate) | **REJECTED** — dismissals only (959 events, all Red/YellowRed); no yellow target; reds are a rare event (0.25/match in the events era, 0 after 2024) with no reliability evidence. |
| R13 | Momentum | **NOT PRE-MATCH** — an in-match/live quantity in this payload. |

## §4 Consumption map

| Candidate | Base inputs | Variant-arm features |
|---|---|---|
| G-RU2 | X1 (goals-only) | SHRINK (§2 component + X2 motivation) |
| S-RU2 | — | NOT BUILDABLE (X5 absent) |
| C-RU2 | — | NOT BUILDABLE (X5/X9 absent) |
| K-RU2 | — | NOT BUILDABLE (X5/X8 absent) |
| T-RU2 | — | NOT BUILDABLE (X4/X6 absent) |
