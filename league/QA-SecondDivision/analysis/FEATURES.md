# Phase 3.5 — Data Processing / Feature Engineering (QA-SecondDivision)

Consumption rule (J1 template, unchanged): `MODEL_DESIGN.md` may use only
the features defined in §1 of this document, plus the architectural
components delimited in §2. Everything in §3 is rejected — explicitly, with
its reason — and may not re-enter through a later phase. A feature not listed
anywhere here is not eligible; adding one requires a new reliability check
and an amendment to this file.

Global causality contract (J1 FEATURES.md, applies verbatim): features use
only matches with kickoff strictly before the target match's kickoff;
trailing windows or expanding-with-decay fits; ratios are ratios of sums;
fitted state obeys the signed-age rule; where a window cannot be filled the
feature is NaN and the arm that needs it is inactive for that match — never
silently filled.

## §1 Accepted features

### X1 — Blend observation pair (goals-model training input)
- **Definition**: per past match, the pair (goals, team xG) entering the
  Dixon-Coles fit with the production blend weight; xG = stats-feed
  `expected_goals` (All period).
- **Availability in THIS league**: goals — all seasons. xG — **nowhere**
  (zero `expected_goals*` entries in any of 141 payloads; no shotmap).
  Every fit is goals-only (the reference blend's documented fallback).
- **Verdict**: ADOPTED as goals-only fallback.
- **Justification**: F1 (levels) + the production blend's own gate history.

### X2 — Mover tier offset (prior for promoted / relegated clubs)
- **Definition**: J1 FEATURES.md §1 X2 verbatim — a club whose previous
  completed season was in a different tier has its rating prior at season
  entry shifted by a tier-step offset, estimated inside the dev fit from
  historical mover transitions.
- **Availability in THIS league**: **no within-league mover history exists
  before the G virgin** (2024/2025 is the first warehouse season; F4).
  The offset is therefore taken as a frozen warehouse prior from the parent
  league QA-QatarStars (PREREG_G_QA, dev-measured on 4 transitions):
  attack exponent −0.2391, defence exponent −0.1947 (log factors of GF
  −0.356 / GA +0.360 against the QA dev mean team goals 1.6742/match).
  It is a prior, not a within-league estimate — recorded here, not adjusted.
- **Verdict**: ADOPTED for G-QASD's ENTRANT arm only (frozen QA priors).
- **Leakage guard**: the offset is a constant fixed before fitting; it never
  uses any QA-SD virgin-season outcome.

### X3 — Set-play xG share and rate (trailing)
- **Verdict**: DROPPED — no `expected_goals*` key exists in any payload.

### X4 — xG per shot (trailing)
- **Verdict**: DROPPED — no shotmap exists in any payload.

### X5 — Trailing target-rate means (naive / ensemble components)
- **Definition**: J1 FEATURES.md §1 X5 verbatim — the team's trailing-10
  mean of the candidate's own target (SOT, corners, unified yellows, total
  shots) and the corresponding conceded mean; the naive component of the
  reference architectures and the harness's naive baseline.
- **Window**: trailing 10 team matches, strictly pre-match; fewer than 6 of
  the 10 carrying the stat ⇒ NaN (arm inactive for that match).
- **Availability in THIS league**: SOT/corners/shots/yellows — 2024/2025
  stats era (rounds 6–14) onward; the stat-less rounds 1–5 of 2024/2025
  degrade trailing windows to NaN by the rule above (this is absorbed by
  the warm-up design, not patched).
- **Verdict**: ADOPTED for S/C/T/K Gate Zero (and as the naive baseline
  everywhere). **Reliability caveat (F2)**: no trait in this league clears
  a reliability bar (n=8–9 teams; SOT/shots weak-positive, corners/goals/
  yellows zero-or-negative). X5 is adopted on the reference architectures'
  validation history, not on a measured trait in this league; the dev gate
  arbitrates.
- **Justification**: F1/F2 + the reference architectures' own validation history.

### X6 — Attacking xGOT per shot (trailing, era-guarded)
- **Verdict**: DROPPED — no shotmap / xGOT exists in any payload.

### X7 — Opp-box touches for / against (trailing)
- **Verdict**: DROPPED — the `touches_opp_box` key does not exist in any
  payload (verified in the raw-JSON scan; the key is absent from all 33
  stats keys per period).

### X8 — Referee yellow rate (trailing)
- **Verdict**: DROPPED — 0 named referees in both dev seasons (F6); 1 named
  match in 2026/2027 cannot support a trailing rate.

### X9 — Reference territorial covariates (corners Gate Zero arm)
- **Definition**: J1 FEATURES.md §1 X9 verbatim — trailing means of stats-feed
  `BallPossesion` and `big_chance` for/against, production `model_corners_v3`'s
  multiplier covariates, carried unchanged so Gate Zero is the true
  production pattern.
- **Availability in THIS league**: `BallPossesion` exists in all stats matches
  (123/123); `big_chance` exists as a key but is **0/0 in every match**
  (degenerate — DATA_UNDERSTANDING). The possession covariate is carried;
  the big-chance covariate is carried as a zero column (it contributes
  nothing; its beta grid is still run unchanged so Gate Zero is the
  unmodified production pattern, and the engine records that the covariate
  is degenerate in this league rather than silently dropping it).
- **Verdict**: ADOPTED (possession live, big_chance degenerate-but-carried).

## §2 Architectural components — explicitly NOT features

(J1 FEATURES.md §2, applies verbatim.) Ratings, home advantage, Dixon-Coles
rho, NB sizes are fitted parameters of the shared architecture, not
covariates. v5's Beta-Binomial on-target ratio is a fitted latent component
of the S-QASD reference architecture; its presence in Gate Zero is exactly
what the RS arm tests (prior P 200 → 20,000). League half-share constants
(goals 0.4589, SOT 0.4194, corners 0.4495, shots 0.4456, yellows 0.3151)
are frozen constants for report-style splits, per F3 — not features, no team
dimension, never "improved" into per-team quantities. League base rates /
naive baselines belong to the evaluation harness, not to any model.

## §3 REJECTED features (explicit; reason recorded for each)

| # | Feature | Verdict / reason |
|---|---|---|
| R1 | Team first-half shares (goals, SOT, corners, shots, yellows) | **NOISE** — F3: true variance ≈ 0 for goals/SOT/shots (0.0), negligible for corners (0.010); the halves book stays closed. (Event-yellows true SD 0.089 is a known imperfection of the frozen K constant, not a modelling signal at n=56.) |
| R2 | Trailing finishing (goals − xG) | **IMPOSSIBLE** — no xG exists. |
| R3 | Trailing conversion (goals / shot) as a covariate | **REJECTED** — no reliability evidence in this league (F2: goals-for r ≈ −0.7, shots-for positive but n=9); outcome-contaminated by construction. |
| R4 | Standalone trailing on-target rate (SOT / shots) | **NOISE** — no reliability evidence; distinct from v5's internal ratio component (§2). |
| R5 | Defensive xGOT per shot | **IMPOSSIBLE** — no shotmap / xGOT exists. |
| R6 | Lineup / absence features (star-absence, XI strength, top-scorer availability) | **CLOSED** — the V10 protocol result stands league-wide (star absence does not cut SOT); lineups exist in 141/141 matches here but no new reliability evidence is offered, and the agreed reopening standard is not met. |
| R7 | Top-shooter concentration share as a team trait | **NO EVIDENCE** — never reliability-tested as a trait. Ineligible until its own EDA-grade check exists. |
| R8 | Formation / coach features | **NO EVIDENCE** — present in the payload (formations in 141/141) but no reliability check was run; ineligible, not "promising". |
| R9 | Standings position, h2h, teamForm snapshots | **LEAKAGE** — `content.table`/`h2h` are post-match snapshots of the target match itself. |
| R10 | Attendance | **LEAKAGE / NOT PRE-MATCH** — the payload's figure is the actual crowd, known only after the match. |
| R11 | First-goal and other game-state traits | **NOT PRE-MATCH** — descriptive in-match facts only. |
| R12 | Red-card rates (as target or covariate) | **REJECTED** — 0.07–0.14 per match is a rare-event count; no reliability evidence; the production cards design excludes reds as a target as well. |
| R13 | Momentum | **NOT PRE-MATCH** — an in-match/live quantity in this payload. |

## §4 Consumption map (design ← features)

| Candidate | Base inputs | Variant-arm features |
|---|---|---|
| G-QASD | X1 (goals-only), X2 (frozen QA priors) | ENTRANT (X2) |
| S-QASD | X5 (SOT naive + ratings observations) | RS (BB-prior arm, §2 component) |
| C-QASD | X5 (corners naive), X9 (Gate Zero multiplier) | — (X7 dropped: no touches_opp_box) |
| K-QASD | X5 (yellows naive + ratings) | — (X8 dropped: no referees in dev) |
| T-QASD | X5 (shots naive + ratings observations) | — (family arms A/B/C are architectural variants, §2) |
