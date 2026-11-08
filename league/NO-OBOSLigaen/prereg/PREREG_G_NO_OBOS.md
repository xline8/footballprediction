# Pre-registration — G-NO-OBOS (NO-OBOSLigaen goals model)

Frozen: 2026-11-10, before any fitting. Branch `build/no-obos`.
Design authority: `league/NO-OBOSLigaen/analysis/MODEL_DESIGN.md` §1;
features per `league/NO-OBOSLigaen/analysis/FEATURES.md` (X1 goals-only
base; SHR arm; X2 arm); evidence per `analysis/EDA.md` (F1/F4/F11).
Reference: production Dixon-Coles pattern via the J1 engine
`league/J1/engine/goals/` (dc.py copied unmodified, as in NO-Eliteserien).

## Target and lines
- Targets: FT goals from `league/NO-OBOSLigaen/data/no_obos_matches.csv`.
- Metrics: 1X2 log-loss, RPS, OU log-loss. **Primary line OU 2.5**
  (dev over-rate 62.19%). Dev gate and virgin legs are read on the
  **OU 2.5 log-loss** (with 1X2 LL/RPS reported; the G-J1 precedent
  gates goals on OU calibration + LL legs as below).

## Reference architecture (all arms share; frozen constants)
- Dixon-Coles fit as G-J1: iterative multiplicative updates, 14 sweeps,
  damping 0.7, +0.25 smoothing, home advantage fitted (init 0.28),
  score matrix MAXG=10, production `tau`; rho from grid
  (0.0, −0.05, −0.10, −0.15) by weighted goals LL.
- Observation (X1): **goals only** — no xG exists in this league's feed
  in any season, so the production blend's documented goals-only
  fallback is the whole observation (the G-J2/G-J3 situation). No
  blend weight applies.
- Time decay half-life 270 days, frozen. Fit scope for target season
  S: all matches strictly before S's first match date (expanding,
  season-blocked, one fit per target season).
- All matches are regular-season (phase is not a filter).

## Arms
1. **Gate Zero (GZ)** — the unmodified reference. Teams unseen in
   training start at the league mean (a = d = 0).
2. **Arm SHR (thin-team shrinkage)** — Gate Zero plus exactly one
   change: when predicting a match, for each team with fewer than 8
   matches in the training window, that team's scoring lambda is
   shrunk halfway to the league level: `lam_t' = 0.5·lam_t +
   0.5·mu`, where mu is the fit's decay-weighted mean goals per
   team-match and lam_t is the team's predicted goals in this match.
   Both lambdas are adjusted independently by their own team's count.
   (Pre-registered response to the G-J2 post-mortem: unmodified DC
   gives extreme lambdas to 1–2-match teams in season openers; in
   this league the thin teams are entrants from 2. divisjon — F4.)
3. **Arm X2 (mover tier offset)** — Arm SHR plus the mover offset for
   Eliteserien-relegated entrants (X2, F4), constructed as follows
   and in no other way. For target season S, let T(S) be the set of
   completed transitions before S: every season s < S and every club
   that played in NO-Eliteserien in s−1 and in OBOS in s. From those
   transitions compute, pooled as ratios of sums over entrant
   team-matches, `d_att = (entrant GF per match − league team-goal
   mean of season s)` and `d_def = (entrant GA per match − league
   team-goal mean of season s)`, averaged over transitions weighted
   by entrant team-matches. When predicting a match in season S
   involving a club that is an Eliteserien entrant **in season S**
   (Eliteserien in S−1, OBOS in S, first OBOS season only), after the
   SHR adjustment that club's scoring lambda is multiplied by
   `(mu + d_att)/mu` and its opponent's scoring lambda by
   `(mu + d_def)/mu`, where mu is the current fit's decay-weighted
   mean goals per team-match. Multipliers are clamped to [0.5, 2.0].
   If T(S) is empty (target season 2022: no in-corpus transition is
   complete before it), X2 ≡ SHR for that season. Entrants from
   2. divisjon never receive the offset (no parent corpus — F4);
   they are covered by SHR only. The offset used for season S is
   estimated only from transitions completed before season S (the
   FEATURES X2 leakage guard).

## Baselines
- **Climatology**: for target season S, pooled outcome rates (H/D/A)
  and OU2.5 over-rate of all seasons strictly before S.

## Dev protocol
- Training starts with 2021; evaluation seasons 2022, 2023, 2024,
  2025 (n=960). The dev harness must not read 2026 rows at all.

## Virgin protocol
- Virgin window: season 2026 (complete regular season, n=240), read
  ONCE, only for arms passing the dev gate, after dev results are
  frozen. Fit = all matches before the first 2026 match. Virgin
  climatology: pooled 2021–2025 rates.
- Virgin calibration leg is read on OU 2.5: |mean P(over 2.5) −
  actual over-rate|.

## GATE LEGS (verbatim, frozen — identical across the program)

Dev gate — pooled dev LL at the primary line beats BOTH baselines (league base rate; naive trailing-10 / climatology), else arm dead, no virgin read. Virgin legs — (i) LL ≤ Gate Zero's and ≤ best baseline's; (ii) calibration |mean P(over) − actual| ≤ 1.0pp, SE reported, breach within 1 SE = PROVISIONAL PASS; (iii) dev per-season sign check for both-pass (variant dev LL ≤ Gate Zero's in at least half the dev seasons; Gate Zero exempt). Both-pass: both → lower pooled virgin LL ships; one → ships; none → FAIL. Ties → simpler arm (Gate Zero first). If Gate Zero fails its own dev gate, the variants are moot — verdict FAIL regardless of variant dev numbers, and the virgin window is not read.

For this candidate the "primary line" in the gate text is OU 2.5 and
LL means the OU 2.5 log-loss; leg (iii) is read on OU 2.5 LL per dev
season. 1X2 LL/RPS are reported for the record and carry no gate.

## Forbidden
Halves modelling (F3); finishing/form features (F6); absence features
(F10); snapshot features; imported tier offsets (R14); any feature
outside FEATURES.md §1.

## Outputs
- Engine: `league/NO-OBOSLigaen/engine/goals/` (own code).
- `results_dev.json` (+ CSV), `results_virgin.json`,
  `fitted_params_virgin.json` in the engine dir.
- Virgin predictions: `league/NO-OBOSLigaen/predictions/g_no_obos_virgin_predictions.csv`
  — shipped arm (Gate Zero's if nothing ships, labelled), one row per
  2026 match: match_id, date, teams, actual goals, lam_home,
  lam_away, P(H/D/A), P(over 2.5), plus 1H/2H OU ladders derived
  presentation-only from the FT lambdas via the frozen goals constant
  0.440 (1H lambdas = 0.440·lam, 2H = 0.560·lam, Poisson at 1H lines
  0.5/1.5 and 2H lines 1.5/2.5). Halves are never fitted.
- Verdict: `league/NO-OBOSLigaen/reports/G_NO_OBOS_VERDICT.md`.

Production code and data are untouched. No push. No merge.
