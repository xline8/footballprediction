# Phase 3.5 — Data Processing / Feature Engineering

Consumption rule (as J1): `MODEL_DESIGN.md` may use only the features defined in §1 of this document,
plus the architectural components delimited in §2. Everything in §3 is rejected — explicitly, with its
reason — and may not re-enter through a later phase. A feature not listed anywhere here is not eligible;
adding one requires a new reliability check and an amendment to this file.

## Global causality contract (applies to every feature below)

1. For a target match M, a feature is computed **only from matches with kickoff strictly before M's
   kickoff**, in the same league unless the feature says otherwise. The target match's own payload
   contributes nothing except static fixture facts (the two team ids and venue).
2. Windows are **trailing** (the team's most recent N matches before M) or **expanding-with-decay**
   inside a rating fit. Window lengths and minimum-sample rules are fixed per candidate in its
   pre-registration; where a window cannot be filled, the feature is **NaN and the variant arm that
   needs it is inactive for that match** — never silently filled with the match's own-era average
   computed including M or later matches.
3. Ratio features are **ratios of sums** over the window (as in the EDA reliability checks), never means
   of per-match ratios.
4. Fitted state obeys the production signed-age rule: a state fitted on data after M's kickoff is never
   used for M.
5. Attenuation honesty: EDA reliabilities were measured on career-pooled half-samples (~50–100 matches
   per team). Trailing windows of 10–25 matches will show **attenuated** versions of the same traits.
   A trait that is NOISE at career scale (r ≈ 0) cannot become signal at window scale.

## §1 Accepted features

### X1 — Blend observation pair (goals-model training input), goals-only here
- **Definition**: per past match, the goals entering the Dixon-Coles fit. The production blend is
  0.5·goals + 0.5·xG with a goals-only fallback; this league has **no xG anywhere**, so every match
  enters goals-only — the reference blend's own documented fallback, not a new design.
- **Window**: training observations only; the fit for any prediction uses matches strictly before kickoff.
- **Availability**: goals — all seasons, all matches (FT score from `header.teams[].score`).
- **Justification**: F2 (goals traits reliable: for r = 0.795, against r = 0.793) + the production
  blend's own gate history. F1 (levels/drift) justifies per-league fitting with time decay.

### X2 — Cross-tier priors for movers — DROPPED (no data)
- Costa Rica has **no other league in the warehouse** (no parent/sibling tier exists for a newcomer
  prior). There is no second-tier corpus to measure a tier gap from, and inventing one is forbidden.
  Promoted teams (one per season, F5) start at the league mean in Gate Zero, as the reference does
  for unseen teams. The G-J2 thin-history shrinkage variant is also not applicable: no team ever sits
  in the 1–9 prior-match band (F5 — each target season's only thin-history team has exactly 0 prior
  matches and is already at the mean).

### X5 — Trailing target-rate means (naive / ensemble components)
- **Definition**: the team's trailing-10 mean of the candidate's own target (goals, yellows) and the
  corresponding conceded mean — the naive component of the reference architectures and the harness's
  naive baseline. Sources: Phase 2 columns (`home_goals`/`away_goals`, `yellow_home`/`yellow_away`).
- **Window**: trailing 10 team matches, strictly pre-match. If fewer than 6 of the 10 are available,
  the feature is NaN for that match.
- **Availability**: goals — all seasons; yellows — **reliable era only (2023/2024 onward)**. A trailing
  window reaching into the broken card-feed era degrades to NaN by the minimum rule.
- **Justification**: F2 (goals-for r = 0.795/0.793; yellows-for r = 0.621/0.614) + the reference
  architectures' own validation history.

### X3 / X4 / X6 / X7 / X9 — DROPPED (no data)
- All five need stats-feed or shotmap keys (`expected_goals*`, `expected_goals_set_play`,
  `expectedGoalsOnTarget`, `touches_opp_box`, `BallPossesion`, `big_chance`). `content.stats` is null
  in every match and `shotmap.shots` is empty. There is nothing to adopt, and no proxy is substituted.

### X8 — Referee yellow rate — DROPPED (no data)
- Referee identity (`infoBox.Referee.text`) is empty in 1,328/1,350 matches (F6). No referee feature,
  no referee arm.

## §2 Architectural components — explicitly NOT features

- **Ratings, home advantage, Dixon-Coles rho, NB sizes** are fitted parameters of the shared
  architecture (justified by F1/F2 at the architecture level), not covariates; they are estimated by
  the fit, under the signed-age rule.
- **League half-share constants** (CR: goals 0.460, yellows 0.379) are frozen constants for
  report-style splits, per F3. They are not features, carry no team dimension, and may not be
  "improved" into per-team or per-match quantities.
- **League base rates / naive baselines** belong to the evaluation harness, not to any model.

## §3 REJECTED features (explicit; reason recorded for each)

| # | Feature | Verdict / reason |
|---|---|---|
| R1 | Team first-half shares (goals, yellows) | **NOISE** — F3: true variance ≈ 0 for goals (−0.0011) and no team trait for yellows (split-half r = −0.46). The halves book stays closed. |
| R2 | Trailing finishing (goals − xG) / conversion / on-target rate | **UNMEASURABLE** — no xG, no shots, no SOT in this corpus. Not "noise", not "promising": absent. |
| R3 | Cross-tier mover priors (X2) | **NO DATA** — no second tier in the warehouse; do not invent one. |
| R4 | Referee strictness (X8) | **NO DATA** — F6: identity absent in 1,328/1,350 matches. |
| R5 | Set-play / xGOT / box-touch / possession / big-chance covariates (X3/X4/X6/X7/X9) | **NO DATA** — stats feed null everywhere. |
| R6 | Lineup / absence features | **NO EVIDENCE** — lineups exist in the payload but no reliability check was run; ineligible, not "promising". (The top-5 V10 null stands as background; nothing here reopens it.) |
| R7 | Red-card rates (as target or covariate) | **REJECTED** — 0.22 per match is a rare-event count; no reliability evidence; the production cards design excludes reds as a target as well. |
| R8 | Standings position, h2h, teamForm snapshots | **LEAKAGE** — `content.table`/`h2h` are post-match snapshots of the target match itself. |
| R9 | Attendance | **LEAKAGE / NOT PRE-MATCH** — the payload's figure is the actual crowd, known only after the match. |
| R10 | First-goal and other game-state traits | **NOT PRE-MATCH** — descriptive in-match facts only. |
| R11 | Momentum | **NOT PRE-MATCH** — an in-match/live quantity in this payload. |
| R12 | Formation / coach features | **NO EVIDENCE** — present in the payload but no reliability check was run; ineligible. |

## §4 Consumption map (design ← features)

| Candidate | Base inputs | Variant-arm features |
|---|---|---|
| G-CR | X1 (goals-only), X5 (goals naive) | — (Gate Zero only; X2 vacuous, see §1) |
| K-CR | X5 (yellows naive + ratings) | — (Gate Zero only; X8 absent, see §1) |
| SOT / corners / total shots | — | NOT candidates (targets do not exist) |
