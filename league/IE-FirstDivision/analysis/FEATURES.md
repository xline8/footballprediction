# Phase 3.5 — Data Processing / Feature Engineering

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
   contributes nothing except static fixture facts (the two team ids
   and venue).
2. Windows are **trailing** (the team's most recent N matches before
   M) or **expanding-with-decay** inside a rating fit. Where a window
   cannot be filled, the feature is **NaN and the variant arm that
   needs it is inactive for that match** — never silently filled with
   the match's own-era average computed including M or later matches.
3. Ratio features are **ratios of sums** over the window, never means
   of per-match ratios.
4. Fitted state obeys the production signed-age rule: a state fitted
   on data after M's kickoff is never used for M.
5. Attenuation honesty: EDA reliabilities were measured on
   career-pooled half-samples. Trailing windows of 10–25 matches will
   show **attenuated** versions of the same traits. A trait that is
   NOISE at career scale (r ≈ 0) cannot become signal at window scale.

## §1 Accepted features

### X1 — Blend observation pair (goals-model training input)
- **Definition**: per past match, the pair (goals, team xG) entering
  the Dixon-Coles fit with the production blend weight; goals from
  `header.status.scoreStr`.
- **Window**: training observations only; the fit for any prediction
  uses matches strictly before kickoff (contract §1.1/§1.4).
- **Availability**: goals — all seasons. xG — **nowhere in this
  corpus** (no stats feed, no shotmap, any season). The model is
  **goals-only throughout** — the reference blend's documented
  fallback, not a new design. This is the many-precedent goals-only
  case (cf. G-IE, G-J2/G-J3).
- **Justification**: F2 (goals traits reliable: for r=0.824, against
  r=0.961) + the production blend's own gate history. F1 justifies
  per-league fitting with time decay.

### X2 — Mover tier offset (prior for relegated clubs)
- **Definition**: for a club whose previous completed season was in
  the Premier Division (the tier above), its rating prior at season
  entry is shifted by a tier-step offset: attack up / defence down
  when moving down. The offset magnitudes are **frozen constants
  from the EDA**: attack **+0.23** goals/match, defence **−0.27**
  goals/match (EDA F4 — mean first-season deltas of the six
  relegated arrivals in dev, 2022–2025). They are plausibility
  magnitudes measured before fitting, not parameters tuned on dev.
- **Raw inputs**: tier membership by season, derived from the two
  leagues' tables themselves (which league's table each club appears
  in per season, keyed by FotMob team id; sibling table:
  `league/IE-PremierDivision/data/ie_matches.csv`).
- **Leakage guard**: the offset used for season S is the frozen EDA
  magnitude; a club's own current-season matches never inform its
  own entry prior. Brand-new clubs (no prior season in either tier —
  Kerry FC 2023, n=1) receive **no offset** and start at the league
  mean: one observation cannot support a prior.
- **Availability**: this league (relegated arrivals only — nothing
  arrives from below, there is no tier below).
- **Justification**: F4 (**SIGNAL-CANDIDATE, weak, n=6** — four of
  six score more, five of six concede less; one mover, Finn Harps,
  breaks the pattern outright). The arm is gated, not assumed.

### X5 — Trailing target-rate means (naive / ensemble components)
- **Definition**: the team's trailing-10 mean of the candidate's own
  target and the corresponding conceded mean.
- **Availability**: **not applicable to the goals candidate** — the
  DC reference architecture does not consume a trailing-mean
  component, and its harness baseline is climatology, not
  trailing-10. For the count markets (SOT/corners/cards/shots) X5
  cannot be built because no target exists (see §3). X5 is recorded
  here for template completeness and consumed by nothing in this
  league.

## §2 Architectural components — explicitly NOT features

- **Ratings, home advantage, Dixon-Coles rho, NB sizes** are fitted
  parameters of the shared architecture (justified by F1/F2 at the
  architecture level), not covariates; they are estimated by the
  fit, under the signed-age rule.
- **League half-share constants** (First Division: goals 0.441) are
  frozen constants for report-style splits, per F3. They are not
  features, carry no team dimension, and may not be "improved" into
  per-team or per-match quantities.
- **League base rates / naive baselines** belong to the evaluation
  harness, not to any model.
- **The SHRINK arm is NOT a feature and NOT included.** G-IE proved
  it a no-op under season-blocked fits: a promoted/relegated club has
  0 prior in-league matches at fit time, so an n/6 shrinkage on
  fitted ratings (which bites only at 1–5 prior matches) never
  engages — Gate Zero and SHRINK were numerically identical in every
  dev season. Including it here would be theatre. The new-team
  failure mode it was meant to address is covered, if at all, by the
  X2 prior offset, which *does* bite at season entry.

## §3 REJECTED features (explicit; reason recorded for each)

| # | Feature | Verdict / reason |
|---|---|---|
| R1 | Team first-half shares (goals) | **NOISE** — F3: true variance 0.000 pooled (n=763). The halves book stays closed. |
| R2 | Trailing finishing (goals − xG) | **NO DATA** — no xG anywhere in the corpus. |
| R3 | Trailing conversion (goals / shot) | **NO DATA** — no shots anywhere. |
| R4 | Standalone trailing on-target rate (SOT / shots) | **NO DATA** — no SOT/shots anywhere. |
| R5 | Defensive xGOT per shot | **NO DATA** — no shotmap anywhere. |
| R6 | Lineup / absence features | **NO DATA + CLOSED** — no lineups in any payload; V10 null stands. |
| R7 | Top-shooter concentration share | **NO DATA** — no player stats anywhere. |
| R8 | Formation / coach features | **NO DATA** — no lineups anywhere. |
| R9 | Standings position, h2h, teamForm snapshots | **LEAKAGE** — `content.table`/`h2h` are post-match snapshots of the target match itself. |
| R10 | Attendance | **LEAKAGE / NOT PRE-MATCH** — the payload's figure is the actual crowd, known only after the match. |
| R11 | First-goal and other game-state traits | **NOT PRE-MATCH** — descriptive in-match facts only. |
| R12 | Red-card rates (as target or covariate) | **REJECTED** — 0.20/match is a rare-event count; no reliability evidence; the production cards design excludes reds as a target as well. The only card data in this corpus *is* reds. |
| R13 | Momentum | **NOT PRE-MATCH** — an in-match/live quantity in this payload. |
| R14 | X3 set-play xG share/rate | **NO DATA** — no xG splits anywhere. |
| R15 | X4 xG per shot | **NO DATA** — no shotmap/xG anywhere. |
| R16 | X6 attacking xGOT per shot | **NO DATA** — no shotmap anywhere. |
| R17 | X7 opp-box touches | **NO DATA** — no stats feed anywhere. |
| R18 | X8 referee yellow rate | **NO DATA** — referee text is empty in 1,028/1,028 matches. |
| R19 | X9 possession / big-chance covariates | **NO DATA** — no stats feed anywhere. |

## §4 Consumption map (design ← features)

| Candidate | Base inputs | Variant-arm features |
|---|---|---|
| G-IEFD | X1 (goals-only) | X2 (relegated-mover offset arm) |
| S-IEFD / C-IEFD / K-IEFD / T-IEFD | — | — (NOT buildable; see `prereg/PREREG_NOT_BUILDABLE.md`) |
