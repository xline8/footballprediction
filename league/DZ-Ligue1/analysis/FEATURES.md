# Step 3.5 — Features: Algeria Ligue 1 (FotMob 516)

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
  every one of the 1,332 payloads (`content.stats` empty), so the
  reference blend's documented fallback applies: matches enter
  goals-only. Goals from `header.status`/`header.teams` (== index
  `score` on 1,332/1,332), all seasons.
- The Dixon-Coles fit itself (ratings, home advantage, rho, time
  decay hl=270) is the §2 architectural component, unchanged.

### X2 — Mover tier offset (prior for promoted / relegated clubs)
- **DROPPED — no parent/sibling exists.** There is no other
  Algerian league in the warehouse (Ligue 1 is the only one), so no
  mover transition is observable and no tier-step offset is
  estimable. Two promoted clubs enter every season (EDA §5 / F4);
  they start at the league mean in Gate Zero. The sanctioned
  thin-data treatment is the SHRINK arm (MODEL_DESIGN §2),
  motivated by the G-J2 post-mortem, not by a measured X2 offset —
  no offset is hard-coded anywhere.

### X3 — Set-play xG share and rate
- **DROPPED — data absent.** `expected_goals_set_play` exists in
  0/1,332 payloads. No reliability check is possible.

### X4 — xG per shot
- **DROPPED — data absent.** No shotmap in 0/1,332 payloads; no
  per-shot `expectedGoals` exists.

### X5 — Trailing target-rate means
- **DROPPED — targets absent.** SOT, corners and yellows exist in
  0/1,332 payloads (stats empty; events carry no SOT/corners and no
  plain Yellow events). There is no trailing mean to compute for any
  candidate. The goals model does not use a trailing-means component
  (its reference architecture is the DC fit, not the v5 ensemble).

### X6 — Attacking xGOT per shot
- **DROPPED — data absent.** No shotmap, no `expectedGoalsOnTarget`
  in any payload.

### X7 — Opp-box touches for / against
- **DROPPED — data absent.** `touches_opp_box` exists in 0/1,332
  payloads.

### X8 — Referee yellow rate
- **DROPPED — data absent.** Referee identity is empty in 1,332/1,332
  payloads (key present, text always `''`) and no yellow target
  exists to rate referees on.

### X9 — Reference territorial covariates (corners Gate Zero)
- **DROPPED — not applicable.** Corners is not a candidate here
  (no target); possession / big-chance keys exist in 0/1,332
  payloads in any case.

## §2 Architectural components — explicitly NOT features

- **Ratings, home advantage, Dixon-Coles rho, time decay** are fitted
  parameters of the shared architecture (justified by EDA §1–§2: the
  league's stable low scoring level with its very large home edge,
  and moderately reliable attack traits with an era-qualified
  defence trait, r=.40/.60 pooled), not covariates. The
  per-season trait wobble (defence r from .78 to .03) is a property
  the dev gate will adjudicate, not a reason to add covariates.
- **League half-share constant (goals 0.4421)** is a frozen constant
  for report-style splits, per EDA §4 (excess variance −0.00039;
  split-half r=−0.05). It is not a feature, carries no team
  dimension, and may not be "improved" into a per-team or
  per-match quantity.
- **League base rates / naive baselines** belong to the evaluation
  harness, not to any model.
- **SHRINK** (MODEL_DESIGN §2) is a prediction-time shrinkage of
  thin-data teams' fitted ratings toward the league mean — a
  component of the variant arm, not a covariate.

## §3 REJECTED features (explicit; reason recorded for each)

| # | Feature | Verdict / reason |
|---|---|---|
| R1 | Team first-half shares (goals, SOT, corners, shots, xG) | **NOISE** — EDA §4: excess variance −0.00039, split-half r=−0.05 for goals; other targets do not exist. Halves book stays closed. |
| R2 | Trailing finishing (goals − xG) | **NO EVIDENCE** — no xG exists; cannot be computed. |
| R3 | Trailing conversion (goals / shot) | **NO EVIDENCE** — no shot counts exist. |
| R4 | Standalone trailing on-target rate | **NO EVIDENCE** — no SOT/shots exist. |
| R5 | Defensive xGOT per shot | **NO EVIDENCE** — no shotmap exists. |
| R6 | Lineup / absence features | **CLOSED** — only 1 match in 1,332 carries starters; there is no lineup data in usable form. V10 protocol already closed this for SOT in production, and it cannot even be tested here. |
| R7 | Top-shooter concentration share | **NO EVIDENCE** — never reliability-tested; no shot data exists. |
| R8 | Formation / coach features | **NO EVIDENCE** — no lineup/player data exists. |
| R9 | Standings position, h2h, teamForm snapshots | **LEAKAGE** — `content.table`/`h2h` are post-match snapshots of the target match itself. |
| R10 | Attendance | **LEAKAGE / NOT PRE-MATCH** — the payload's figure is the actual crowd (and null here in any case). |
| R11 | First-goal and other game-state traits | **NOT PRE-MATCH** — in-match facts only. |
| R12 | Red-card rates (as target or covariate) | **REJECTED** — dismissals only (244 events, all Red/YellowRed, 0 plain Yellows); no yellow target; reds are a rare event (0.18/match) with no reliability evidence. |
| R13 | Momentum | **NOT PRE-MATCH** — an in-match/live quantity in this payload. |

## §4 Consumption map

| Candidate | Base inputs | Variant-arm features |
|---|---|---|
| G-DZ | X1 (goals-only) | SHRINK (§2 component + G-J2-lesson motivation) |
| S-DZ | — | NOT BUILDABLE (X5 absent) |
| C-DZ | — | NOT BUILDABLE (X5/X9 absent) |
| K-DZ | — | NOT BUILDABLE (X5/X8 absent) |
| T-DZ | — | NOT BUILDABLE (X4/X6 absent) |
