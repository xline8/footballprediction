# Pre-registration — G-US (US-MLS goals model)

Frozen: 2026-11-09, before any fitting. Branch `build/us-mls`.
Design authority: `league/US-MLS/analysis/MODEL_DESIGN.md` §1; features per
`league/US-MLS/analysis/FEATURES.md` (X1 base; X3 tilt arm; X2 dropped — F4);
evidence per `league/US-MLS/analysis/EDA.md` (F1/F4/F5/F11). Reference:
production Dixon-Coles pattern via the J1 engine `league/J1/engine/goals/`.

## Target and lines

- Targets: FT goals from `league/US-MLS/data/us_matches.csv`.
- Metrics: 1X2 log-loss, RPS, OU log-loss. **Primary line OU 2.5**
  (dev over-rate 0.584). Dev gate and virgin legs are read on the **OU 2.5
  log-loss** (with 1X2 LL/RPS reported; the G-J1 precedent gates goals on OU
  calibration + LL legs as below).

## Reference architecture (all arms share; frozen constants)

- Dixon-Coles fit as G-J1: iterative multiplicative updates, 14 sweeps,
  damping 0.7, +0.25 smoothing, home advantage fitted (init 0.28), score
  matrix MAXG=10, production `tau`; rho from grid (0.0, −0.05, −0.10, −0.15)
  by weighted goals LL.
- Observation (X1): blend 0.5·goals + 0.5·xG, with the documented goals-only
  fallback where xG is missing.
- Time decay half-life 270 days, frozen. Fit scope for target season S: all
  matches strictly before S's first match date (expanding, season-blocked, one
  fit per target season).
- Regular and playoff matches are in every window; phase is not a filter.

## Arms

1. **Gate Zero (GZ)** — the unmodified reference. Teams unseen in training
   start at the league mean (a = d = 0).
2. **Arm SHR (thin-team shrinkage)** — Gate Zero plus exactly one change: when
   predicting a match, for each team with fewer than 8 matches in the training
   window, that team's scoring lambda is shrunk halfway to the fit's league
   level: `lam_t' = 0.5·lam_t + 0.5·mu`, where mu is the fit's decay-weighted
   mean goals per team-match and lam_t is the team's predicted goals in this
   match. Both lambdas are adjusted independently by their own team's count.
   This addresses expansion clubs with no MLS history — Charlotte at dev-2022
   entry, St. Louis at dev-2023 entry, and San Diego FC entering the VIRGIN
   season 2025 with zero prior matches (F4/F10).
3. **Arm X3** — Arm SHR plus the set-play decomposition tilt (X3, F5 r=0.684),
   constructed exactly as G-J1's X3 arm (`arms.x3_multipliers`: decay-weighted
   open-play/set-play xG for/against, geometric-mean multipliers clamped
   [0.5, 2.0], outer sqrt shrinkage, min 8 xG matches else multiplier 1.0).

## Baselines

- **Climatology**: for target season S, pooled outcome rates (H/D/A) and OU2.5
  over-rate of all seasons strictly before S.

## Dev protocol

- Warm-up 2021; scored dev seasons 2022, 2023, 2024 (n=1532). The dev harness
  must not read 2025 rows at all, and must not read reserved 2026 rows.

## Virgin protocol

- Virgin season 2025 (n=540), read ONCE, only for arms passing the dev gate,
  after dev results are frozen. Fit = all matches before the first 2025 match.
- Virgin calibration leg is read on OU 2.5: |mean P(over 2.5) − actual over-rate|.

## GATE LEGS (verbatim, frozen — identical across the program)

Dev gate — pooled dev LL at the primary line beats BOTH baselines (league base rate; naive trailing-10 / climatology), else arm dead, no virgin read. Virgin legs — (i) LL ≤ Gate Zero's and ≤ best baseline's; (ii) calibration |mean P(over) − actual| ≤ 1.0pp, SE reported, breach within 1 SE = PROVISIONAL PASS; (iii) dev per-season sign check for both-pass (variant dev LL ≤ Gate Zero's in at least half the dev seasons; Gate Zero exempt). Both-pass: both → lower pooled virgin LL ships; one → ships; none → FAIL. Ties → simpler arm (Gate Zero first). If Gate Zero fails its own dev gate, the variants are moot — verdict FAIL regardless of variant dev numbers, and the virgin window is not read.

For this candidate the "primary line" in the gate text is OU 2.5 and LL means the OU 2.5 log-loss; leg (iii) is read on OU 2.5 LL per dev season. 1X2 LL/RPS are reported for the record and carry no gate.

## Forbidden

Halves modelling (F3); finishing/form features (F6); absence features (F10);
snapshot features; imported tier offsets (R14); any feature outside
`FEATURES.md` §1.

## Outputs

- Engine: `league/US-MLS/engine/goals/` (own code).
- `results_dev.json` (+ CSV), `results_virgin.json`,
  `fitted_params_virgin.json` in the engine dir.
- Virgin predictions: `league/US-MLS/predictions/g_us_virgin_predictions.csv`
  — shipped arm (Gate Zero's if nothing ships, labelled), one row per 2025
  match: match_id, date, teams, actual goals, lam_home, lam_away, P(H/D/A),
  P(over 2.5), plus 1H/2H OU ladders derived presentation-only from the FT
  lambdas via the frozen goals constant 0.445 (1H lambdas = 0.445·lam,
  2H = 0.555·lam, Poisson at 1H lines 0.5/1.5 and 2H lines 1.5/2.5).
- Verdict: `league/US-MLS/reports/G_US_VERDICT.md`.
