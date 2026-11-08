# Phase 3.5 — Data Processing / Feature Engineering (AM-PremierLeague)

Consumption rule: `MODEL_DESIGN.md` may use only the features defined
in §1 of this document, plus the architectural components delimited in
§2. Everything in §3 is rejected — explicitly, with its reason — and
may not re-enter through a later phase.

## Global causality contract (applies to every feature below)

1. For a target match M, a feature is computed **only from matches
   with kickoff strictly before M's kickoff**, in the same league
   unless the feature says otherwise. The target match's own payload
   contributes nothing except static fixture facts (the two team ids
   and venue).
2. Windows are **trailing** (the team's most recent N matches before
   M) or **expanding-with-decay** inside a rating fit. Where a window
   cannot be filled, the feature is **NaN and the variant arm that
   needs it is inactive for that match** — never silently filled.
3. Ratio features are **ratios of sums** over the window, never means
   of per-match ratios.
4. Fitted state obeys the production signed-age rule: a state fitted
   on data after M's kickoff is never used for M.
5. Attenuation honesty: EDA reliabilities were measured on
   season-pooled half-samples (~16–18 matches per team). Trailing
   windows of 10 matches will show attenuated versions of the same
   traits. A trait that is NOISE at season scale (r ≈ 0) cannot
   become signal at window scale.

## §1 Accepted features

### X1 — Blend observation pair (goals-model training input)
- **Definition**: per past match, the goals observation entering the
  Dixon-Coles fit. Goals from `header.status.scoreStr` (index
  `score`).
- **Availability**: goals — all seasons. xG — **nowhere in this
  league** (stats null, shotmap empty, 881/881). The fit is
  therefore **goals-only throughout** — the reference blend's
  documented fallback, not a variant.
- **Justification**: F1 (levels high and rising, home advantage
  mostly steady with one inverted season) + F2 (team traits
  STRONG — GF 0.78 / GA 0.76 split-half means — so the fit has
  real team signal to find; the dev gate, not F2, is the
  justification for shipping) + the production blend's own gate
  history.

### X5 — Trailing target-rate means (naive baseline component only)
- **Definition**: the team's trailing-10 mean of goals for and
  against (from Phase 2 columns `home_goals`/`away_goals`), strictly
  pre-match. This is the **naive baseline** in the harness, not a
  model input: naive lambdas = trailing-10 GF mean (home) /
  trailing-10 GA-implied rates, scored as Poisson without DC.
- **Window**: trailing 10 team matches; if fewer than 6 of the 10
  exist, the naive prediction for that match is the league mean.
- **Availability**: goals only. SOT/corners/yellows versions do not
  exist (targets absent).
- **Justification**: F2 + the reference architectures' validation
  history (naive baseline every candidate must beat).

### X2-SHRINK — Thin-history rating shrinkage (variant arm)
- **Definition**: at prediction time, for a team with fewer than 6
  prior in-league matches in the training window, its fitted attack
  and defence ratings are shrunk toward the league mean:
  `a *= n/6`, `d *= n/6`, where n = prior in-league matches in the
  training window (n=0 is identical to Gate Zero's unseen rule).
  This is the sanctioned G-J2-lesson arm (post-mortem: unmodified
  DC gives extreme lambdas to 1–2-match teams in season openers),
  already used as the SHRINK arm in G-AE, G-BA, G-AL and sibling
  preregs.
- **Availability**: every season (1–2 clubs change per season;
  2026/27 brings Sardarapat and Syunik in together).
- **Justification**: F2 (ratings are strong and tiers are steep —
  top +1.17 to bottom −1.42 GD/match — so a new club given an
  extreme fitted rating from a handful of matches is a live risk,
  the opposite of the AL case where the arm was decorative) +
  F4 (no mover offset is estimable, so shrinkage toward the mean
  is the thin-data treatment). Expected to be degenerate under
  season-blocked expanding fits (as in BA/AL: prior counts are 0
  or ≥27) — recorded as a design note, not a defect, if the two
  arms come out identical.

## §2 Architectural components — explicitly NOT features

- **Ratings, home advantage, Dixon-Coles rho, NB sizes** are fitted
  parameters of the shared architecture, not covariates; estimated
  by the fit, under the signed-age rule.
- **League half-share constant** (goals 0.4335, EDA F3) is a frozen
  constant for report-style splits. It is not a feature, carries no
  team dimension, and may not be "improved" into per-team or
  per-match quantities.
- **League base rates / naive baselines** belong to the evaluation
  harness, not to any model.

## §3 REJECTED / DROPPED features (explicit; reason recorded for each)

| # | Feature | Verdict / reason |
|---|---|---|
| X2 | Mover tier offset (cross-tier prior) | **DROPPED — no data.** No Armenian sibling exists in the warehouse; no feeder-tier history from which to estimate an offset. SHRINK (§1) is the thin-data treatment instead. |
| X3 | Set-play xG share and rate | **DROPPED — no data.** No xG splits (no stats at all). |
| X4 | xG per shot (trailing) | **DROPPED — no data.** No shotmap. |
| X6 | Attacking xGOT per shot | **DROPPED — no data.** No shotmap. |
| X7 | Opp-box touches for/against | **DROPPED — no data.** No stats feed. |
| X8 | Referee yellow rate | **DROPPED — no data.** Referee field empty 881/881; yellows do not exist either. |
| X9 | Territorial covariates (possession, big chances) | **DROPPED — no data.** No stats feed. |
| R1 | Team first-half shares | **NOISE** — F3: own-goals split-half mean r ≈ +0.08 (sign-flipping); excess variance −0.0086, true SD ≈ 0.000. Frozen constant only. (The naive match-total definition returns r ≈ 0.83 but is confounded by team strength — binomial-resample null gives r ≈ 0.82 — so it is not evidence.) |
| R2 | Trailing finishing (goals − xG) | **NO DATA** — no xG; not computable. |
| R3 | Trailing conversion (goals / shot) | **NO DATA** — no shots; not computable. |
| R4 | Standalone trailing on-target rate | **NO DATA** — no SOT/shots; not computable. |
| R5 | Defensive xGOT per shot | **NO DATA** — no shotmap. |
| R6 | Lineup / absence features | **NO DATA + CLOSED** — lineups present 0/881 with real content (16 unavailable shells); the V10 star-absence protocol already failed on the top-5 spine and on J1. |
| R7 | Top-shooter concentration share | **NO EVIDENCE** — no player data at all. |
| R8 | Formation / coach features | **NO DATA** — no lineups. |
| R9 | Standings position, h2h, teamForm snapshots | **LEAKAGE** — `content.table`/`h2h` are post-match snapshots of the target match itself. |
| R10 | Attendance | **NO DATA** — Attendance null in 881/881 (and post-match by nature). |
| R11 | First-goal and other game-state traits | **NOT PRE-MATCH** — F12 records HT scores as descriptive only. |
| R12 | Red-card rates (as target or covariate) | **REJECTED** — 0.21/match rare-event count (186 red-family events, 0 yellows); no reliability evidence; production cards design excludes reds as a target. |
| R13 | Momentum | **NOT PRE-MATCH** — an in-match/live quantity in this payload. |

## §4 Consumption map (design ← features)

| Candidate | Base inputs | Variant-arm features |
|---|---|---|
| G-AM | X1 (goals-only) | X2-SHRINK (thin-history shrinkage arm) |
| S-AM / C-AM / K-AM / T-AM | — | — (not buildable; see prereg `PREREG_SCKT_NOT_BUILDABLE.md`) |
