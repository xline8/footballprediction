# Phase 3.5 — Data Processing / Feature Engineering (between EDA and design)

This step exists because leakage usually enters at feature definition,
not at model fitting. **Consumption rule: `MODEL_DESIGN.md` may use
only the features defined in §1 of this document, plus the
architectural components delimited in §2. Everything in §3 is rejected
— explicitly, with its reason — and may not re-enter through a later
phase.** A feature not listed anywhere here is not eligible; adding
one requires a new reliability check and an amendment to this file.

## Global causality contract (applies to every feature below)

1. For a target match M, a feature is computed **only from matches
   with kickoff strictly before M's kickoff**, in the same league
   unless the feature says otherwise. The target match's own payload
   contributes nothing except static fixture facts (the two team ids,
   venue, and — for X8 — the appointed referee's identity).
2. Windows are **trailing** (the team's / referee's most recent N
   matches before M) or **expanding-with-decay** inside a rating fit.
   Window lengths and minimum-sample rules are fixed per candidate in
   its pre-registration; where a window cannot be filled, the feature
   is **NaN and the variant arm that needs it is inactive for that
   match** — never silently filled with the match's own-era average
   computed including M or later matches.
3. Ratio features are **ratios of sums** over the window (as in the
   EDA reliability checks), never means of per-match ratios.
4. Fitted state obeys the production signed-age rule: a state fitted
   on data after M's kickoff is never used for M.
5. Attenuation honesty: EDA reliabilities were measured on
   career-pooled half-samples (~50–100 matches per team). Trailing
   windows of 10–25 matches will show **attenuated** versions of the
   same traits. A trait that is NOISE at career scale (r ≈ 0) cannot
   become signal at window scale; a trait that is strong at career
   scale may still fail at window scale — which is what the dev
   walk-forward gate is for.

## §1 Accepted features

### X1 — Blend observation pair (goals-model training input)
- **Definition**: per past match, the pair (goals, team xG) entering
  the Dixon-Coles fit with the production blend weight; xG =
  stats-feed `expected_goals` (`content.stats.Periods.All`, key
  `expected_goals`, home/away as listed). Goals from
  `header.status.scoreStr`.
- **Window**: training observations only; the fit for any prediction
  uses matches strictly before kickoff (contract §1.1/§1.4).
- **Availability**: goals — J1/J2/J3, all seasons. xG — **J1 2022+
  only**; matches without xG enter goals-only (the reference blend's
  documented fallback). J2/J3 fits are goals-only throughout.
- **Justification**: F11 (FotMob xG calibrated for J1, goals/xG
  0.98–1.08 per season) + the production blend's own gate history.
  F1 (levels/drift) justifies per-league fitting with time decay.

### X2 — Mover tier offset (prior for promoted / relegated clubs)
- **Definition**: for a club whose previous completed season was in
  a different tier of the same system, its rating prior at season
  entry is shifted by a tier-step offset (attack down / defence up
  when moving up; mirrored when moving down). The offset is a
  **parameter estimated inside the dev fit** from historical mover
  transitions; the EDA's descriptive magnitudes (J2→J1: GF −0.56,
  GA +0.51 per match; J3→J2 the same) are the plausibility range,
  not constants to hard-code.
- **Raw inputs**: tier membership by season, derived from the corpus
  itself (which league's table each club appears in per season,
  keyed by FotMob team id).
- **Leakage guard**: the offset used for season S is estimated only
  from transitions completed **before** season S; a club's own
  current-season matches never inform its own entry prior.
- **Availability**: J1 (movers from/to J2), J2 (both steps), J3
  (movers from/to J2).
- **Justification**: F4 (**SIGNAL**, symmetric at both steps,
  n=9–13 movers per direction).

### X3 — Set-play xG share and rate (trailing)
- **Definition**: over the team's trailing window,
  `sp_share = Σ expected_goals_set_play / Σ expected_goals` and
  `sp_rate = Σ expected_goals_set_play / matches`, from the stats
  feed (`content.stats.Periods.All` keys `expected_goals_set_play`,
  `expected_goals`). Open-play analogues are the complements and
  carry no extra information beyond the pair (share, total).
- **Window**: trailing, ratio of sums; minimum 8 window matches with
  xG present, else NaN (arm inactive).
- **Availability**: **J1 2022+ only** (xG splits do not exist in J2/J3
  or in J1 2021).
- **Justification**: F5 (**SIGNAL-CANDIDATE**, split-half r=0.621
  for the share). Consumed by G-J1's decomposition arm only.

### X4 — xG per shot (trailing)
- **Definition**: `Σ sm_xg / Σ sm_shots` over the team's trailing
  window, where `sm_*` are the Phase 2 shotmap aggregates over
  **regulation shots only** (shootout attempts excluded, Phase 2
  rule 5) — equivalently Σ per-shot `expectedGoals` / shot count
  from `content.shotmap.shots`.
- **Window**: trailing, ratio of sums; minimum 8 window matches with
  shotmap, else NaN.
- **Availability**: **J1 2022+ only**.
- **Justification**: F6 (**SIGNAL-CANDIDATE**, split-half r=0.437 —
  shot *selection* quality). Consumed by S-J1's quality-input arm.

### X5 — Trailing target-rate means (naive / ensemble components)
- **Definition**: the team's trailing-10 mean of the candidate's own
  target (SOT, corners, or unified yellows) and the corresponding
  conceded mean — the naive component of the reference architectures
  (v5's ensemble; corners/cards analogues) and the harness's naive
  baseline. Sources: Phase 2 columns (`ShotsOnTarget_*`, `corners_*`,
  unified `yellow_*` with its documented provenance).
- **Window**: trailing 10 team matches, strictly pre-match. If fewer
  than 6 of the 10 carry the stat (feed windows, F13), the feature
  is NaN for that match.
- **Availability**: SOT/corners — J1 all seasons; J2 inside the
  Sep 2021–Sep 2024 stats window only (a trailing window reaching
  past the window's death in Oct 2024 degrades to NaN by the rule
  above — this is precisely why C-J2 is not a candidate); J3 only
  the 62-match 2025 window (unusable in practice). Yellows — J1, J2
  all seasons (J2 via events); J3 never.
- **Justification**: F2 (target traits reliable: SOT-for r=0.76/0.80,
  corners-for 0.65/0.64, yellows-for 0.66/0.51) + the reference
  architectures' own validation history.

### X6 — Attacking xGOT per shot (trailing, era-guarded)
- **Definition**: `Σ sm_xgot / Σ sm_xgot_n` over the team's trailing
  window (Phase 2 aggregates of per-shot `expectedGoalsOnTarget`),
  counting **only matches from the 2025 era onward**, where the
  field is populated for ~all shots.
- **Window**: trailing, ratio of sums; **era guard**: window matches
  before 2025 never count (their xGOT is populated only for
  on-target shots — a different quantity); minimum 8 era-valid
  window matches, else NaN (arm inactive). This makes the feature
  unavailable for predictions before ~mid-2025 by construction.
- **Availability**: **J1, 2025+ era only**. Attacking side only.
- **Justification**: F7 (**SIGNAL-CANDIDATE**, split-half r=0.518,
  23 teams, short era — hence arm status and era guard, not base
  design). Consumed by S-J1's recent-era arm only.

### X7 — Opp-box touches for / against (trailing)
- **Definition**: trailing means of the stats-feed
  `touches_opp_box` (`content.stats.Periods.All`) for the team
  (`_for`) and conceded to opponents (`_against`), per match.
- **Window**: trailing means; minimum 8 window matches with the
  stat, else NaN. (J1 2021 has the stat in only 230/380 matches —
  the minimum rule absorbs that.)
- **Availability**: **J1 only** (the J2/J3 stats blocks never carry
  this key).
- **Justification**: F9 (**SIGNAL-CANDIDATE**: for-trait split-half
  r=0.857; against-trait r=0.687, measured for this step; per-match
  corr with corners 0.471 vs possession 0.286). Consumed by C-J1's
  territorial-multiplier arm.

### X8 — Referee yellow rate (trailing)
- **Definition**: the appointed referee's trailing mean of unified
  yellows per match **within the same league**, shrunk toward the
  league mean with a shrinkage weight fixed in the candidate's
  pre-registration; referees with fewer than 8 prior in-league
  matches take the (shrunk) league mean. Referee identity:
  `content.matchFacts.infoBox.Referee.text`; past-match yellows:
  Phase 2 unified `yellow_*` (stats feed for J1 — with the 2021
  events exception — events for J2).
- **Leakage guard**: only the referee's matches strictly before
  kickoff count. The identity itself is a fixture fact, but the arm
  carries the operational condition from the design: if the
  appointment is not published pre-match in the live pipeline, the
  fixture falls back to the base arm (no imputation of referees).
- **Availability**: J1, J2. **J3: never** (yellows do not exist).
- **Justification**: F8 (**SIGNAL-CANDIDATE**: split-half r=0.646
  pooled tiers; **r=0.649 on the J1+J2-only, yellows-only recheck**
  run for this step). Consumed by K-J1/K-J2's referee arm.

### X9 — Reference territorial covariates (corners Gate Zero arm)
- **Definition**: trailing means of stats-feed `BallPossesion` and
  `big_chance` for/against — production `model_corners_v3`'s
  multiplier covariates, carried unchanged so Gate Zero is the true
  production pattern, not a straw man.
- **Window/availability**: trailing means, min-8 rule; J1 only.
- **Justification**: production adoption evidence; for the record,
  big-chances-for is reliable on this corpus too (split-half
  r=0.738, measured for this step). Possession was not separately
  reliability-tested here; it stands on its production evidence.

## §2 Architectural components — explicitly NOT features

The boundary matters because two rejected items (§3) resemble
components that legitimately exist inside the reference
architectures:

- **Ratings, home advantage, Dixon-Coles rho, NB sizes** are fitted
  parameters of the shared architecture (justified by F1/F2 at the
  architecture level), not covariates; they are estimated by the
  fit, under the signed-age rule.
- **v5's Beta-Binomial on-target ratio** is a *fitted latent
  component* of the S-J1 reference architecture. It is not a
  trailing covariate, and its presence in Gate Zero is exactly what
  S-J1's harder-shrinkage arm tests (F6). This does **not** license
  a standalone trailing on-target-rate covariate — that object is
  R4 below.
- **League half-share constants** (J1: goals 0.412, SOT 0.448,
  corners 0.447, shots 0.455) are frozen constants for report-style
  splits, per F3. They are not features, carry no team dimension,
  and may not be "improved" into per-team or per-match quantities.
- **League base rates / naive baselines** belong to the evaluation
  harness, not to any model.

## §3 REJECTED features (explicit; reason recorded for each)

| # | Feature | Verdict / reason |
|---|---|---|
| R1 | Team first-half shares (goals, SOT, corners, shots, xG) | **NOISE** — F3: true variance ≈ 0 for all five; split-half ≤0.33 contradicted by the variance decomposition. The halves book stays closed. |
| R2 | Trailing finishing (goals − xG) | **NOISE** — F6: split-half r=0.153. |
| R3 | Trailing conversion (goals / shot) as a covariate | **REJECTED** — F6: r=0.338 is weak and the ratio is outcome-contaminated (it prices in the same finishing luck as R2); dominated by X4 + shot volume. |
| R4 | Standalone trailing on-target rate (SOT / shots) | **NOISE** — F6: r=0.06. Distinct from v5's internal ratio component (§2). |
| R5 | Defensive xGOT per shot | **NOISE** — F7: r=0.116. |
| R6 | Lineup / absence features (star-absence, minutes-weighted XI strength, top-scorer availability) | **CLOSED** — F10: V10 protocol replicated on J1, residual +0.04 ≈ control, no dose pattern. The agreed reopening standard (new reliability evidence) was tested for and not met. |
| R7 | Top-shooter concentration share as a team trait | **NO EVIDENCE** — never reliability-tested as a trait (it appeared only inside R6's test). Ineligible until its own EDA-grade check exists. |
| R8 | Formation / coach features | **NO EVIDENCE** — present in the payload (J1/J2 lineups) but no reliability check was run; ineligible, not "promising". |
| R9 | Standings position, h2h, teamForm snapshots | **LEAKAGE** — `content.table`/`h2h` are post-match snapshots of the target match itself. |
| R10 | Attendance | **LEAKAGE / NOT PRE-MATCH** — the payload's figure is the actual crowd, known only after the match. |
| R11 | First-goal and other game-state traits | **NOT PRE-MATCH** — F12 records them as descriptive in-match facts only. |
| R12 | Red-card rates (as target or covariate) | **REJECTED** — 0.08–0.11 per match is a rare-event count; no reliability evidence; the production cards design excludes reds as a target as well. |
| R13 | Momentum | **NOT PRE-MATCH** — an in-match/live quantity in this payload. |

## §4 Consumption map (design ← features)

| Candidate | Base inputs | Variant-arm features |
|---|---|---|
| G-J1 | X1 (blend), X2 | X3 (set-play decomposition arm) |
| G-J2 / G-J3 | X1 (goals-only), X2 | — |
| S-J1 | X5 (SOT naive + ratings observations) | X4 (quality input), X6 (xGOT, era arm); ratio-shrinkage arm per §2 |
| C-J1 | X5 (corners naive), X9 (Gate Zero multiplier) | X7 (box-touch multiplier arm) |
| K-J1 / K-J2 | X5 (yellows naive + ratings) | X8 (referee arm) |
| Total shots (deferred) | — | — (no features consumed until the deferral trigger fires) |
