# Pre-registration — K-J1 (J1 cards model)

Frozen: 2026-11-09, before any fitting. Branch `build/k-j1`.
Design authority: `league/J1/analysis/MODEL_DESIGN.md` §5 (candidate
K-J1) + shared validation frame + §7b; feature per
`league/J1/analysis/FEATURES.md` X8 (referee yellow rate, trailing);
evidence per `league/J1/analysis/EDA.md` F8 (referee strictness
split-half r = 0.646 pooled, r = 0.649 J1+J2 recheck), F13 (coverage),
F14 (frozen cards halves constant 0.383).
Reference implementation: production `model_cards.py` — decayed
team card ratings (venue-split attack/defence), shrinkage to the
league mean, Negative Binomial count distribution; referee NOT used
in production. Its experiment recipe
(`experiments/cards_model/run_cards_experiment.py`) supplies the
baseline definitions and the NB-size estimation formula, unchanged.

## Target and data

- Target: total yellows per match = `yellow_home + yellow_away` in
  `league/J1/data/j1_matches.csv` (unified Phase 2 columns; J1
  stats-first provenance, season 2021 enters via the event feed per
  the design's documented exception, `cards_source = events`).
  Yellows only; reds and second-yellow reds are not counted (design
  §5d). Rows are parsed as floats then int (some seasons store
  `2.0`-style values).
- Corpus mean ≈ 2.34 yellows/match. Primary line **2.5**, secondary
  line **3.5**. Log loss is the binary log loss (natural log) on
  P(over line).
- Processing order is chronological by (`kickoff_utc`, `match_id`).
  Every prediction for a match uses only matches processed strictly
  before it in that order; state updates happen after prediction.

## Reference architecture (Gate Zero; all arms share it)

Copied pattern from `model_cards.py`, constants frozen at the
production values — no search:

- Exponentially decayed rates, half-life **HL = 270 days**: per team
  and venue, yellows for (attack) and yellows conceded (defence);
  decayed league means `mu_h`, `mu_a` (home/away yellows per match).
- Shrinkage to the league mean with prior **K_PRIOR = 8**
  match-equivalents: `shrunk = (s + K·mu) / (w + K)`.
- `exp_home = mu_h · (shrunk att_h(home)/mu_h) · (shrunk def_a(away)/mu_h)`;
  `exp_away` mirrored. Fallback league means before any history:
  `mu_h = 2.15`, `mu_a = 1.95` (production constants; they can only
  bind in the first matches of the warm-up season).
- Match total ~ Negative Binomial(mean = exp_home + exp_away,
  size r), `P(over L)` from the NB CDF exactly as production
  `nb_over`.

## NB size r — estimation discipline (frozen)

Per method (Gate Zero, X8, base-rate baseline, naive baseline), r is
estimated by the production experiment's method of moments on
**causal one-step-ahead residuals of earlier data only**:

    r = Σ μ² / Σ ((y − μ)² − μ),  clipped to [2, 500];
    denominator ≤ 0 → r = 500.

- Dev scoring: r per method is estimated from season **2021**
  (warm-up) causal predictions only, then frozen for the scored dev
  seasons 2022–2025.
- Virgin scoring: r per method is re-estimated from causal
  predictions over seasons **2021–2025** only, then frozen for
  season "2026". No virgin outcome enters any r.

## Arms

1. **Gate Zero** — the unmodified reference above.
2. **Arm X8** — Gate Zero plus the referee strictness covariate
   (feature X8), with the mechanics frozen here:
   - Referee identity per match: `content.matchFacts.infoBox.Referee.text`
     in the warehouse JSON `data_enrichment/fotmob_jleague/J1/<season>/<match_id>.json`
     (key present but text empty = identity unknown). Extracted into
     a referee table (one row per match) before fitting; coverage by
     season is reported in the verdict, not tuned on.
   - Trailing referee rate: over that referee's **J1 matches with
     kickoff strictly before the target match's kickoff**
     (same-league only, per FEATURES X8), ratio of sums:
     `rate_ref = (Σ yellows + K_REF · league_mean) / (n_prior + K_REF)`
     with **K_REF = 8**, where `league_mean` is the expanding
     (non-decayed) mean of total yellows over all J1 matches with
     kickoff strictly before the target kickoff.
   - Minimum history: a referee with **fewer than 8 prior J1
     matches** takes the league mean exactly (multiplier 1.0).
   - Multiplier: `mult = rate_ref / league_mean`, clamped to
     **[0.67, 1.50]**. X8 prediction: `exp_home` and `exp_away` of
     Gate Zero are both multiplied by `mult` (home/away split
     preserved); the total mean is `mult · mu_gate_zero`.
   - Fallback (design §5c(ii), no imputation): if the referee
     identity is unknown **or** prior history < 8, the X8 prediction
     for that match is the Gate Zero prediction exactly. Fallbacks
     are counted, split by reason (unknown identity / thin history).
   - Causality assertion (required in code): for every match where
     the covariate is active, the referee-history structure must
     assert that the most recent match counted has kickoff strictly
     before the target kickoff.

## Baselines (same online pass, identical match set)

- **League base rate**: `mu = mu_h + mu_a`, the decayed league means
  at the match day (production baseline (a); no team information).
- **Naive trailing-10**: production baseline (b) — each team's plain
  mean yellows for/against over its last 10 matches (venues pooled,
  no shrinkage, no decay); `exp_home = (for(home) + against(away))/2`,
  mirrored for away; falls back to the league means when a team has
  no history.

## Dev protocol

- Dev period: seasons 2021–2025, one chronological online
  walk-forward pass (expanding; state updates after each match).
  Season 2021 is warm-up: processed, used for the r estimation
  above, never scored. Scored dev seasons: 2022, 2023, 2024, 2025
  (pooled n = 1,372).
- Metrics per arm/baseline per season and pooled: LL@2.5 (primary),
  LL@3.5 (context), mean predicted P(over 2.5) vs actual over rate.
- The dev harness must not read season "2026" or "2026/2027" rows at
  all (neither targets nor referee histories for scored matches —
  referee history for a dev match is built only from earlier dev
  matches). Virgin data is touched only by the separate virgin step,
  once, after dev results are frozen in the results file.

## Virgin protocol

- Virgin window: season "2026" (n = 200, complete). One fresh online
  pass over 2021–2026; predictions for 2026 use only earlier
  matches; r per the discipline above. Read ONCE, after dev freezes.
- Calibration per arm at 2.5: mean predicted P(over 2.5) − actual
  over rate, with SE = sd(pred_i − y_i)/√n reported.
- The virgin step also reports, per arm: fallback counts for X8 and
  the referee-identity coverage of the virgin window (operational
  check evidence).

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev LL@2.5 beats BOTH baselines (league base rate; naive trailing-10), else arm dead, no virgin read. Virgin legs — (i) LL@2.5 ≤ Gate Zero's and ≤ best baseline's; (ii) calibration |mean P(over 2.5) − actual| ≤ 1.0pp, SE reported, breach within 1 SE = PROVISIONAL PASS; (iii) dev per-season sign check for both-pass. Both-pass: both → lower pooled virgin LL ships; one → ships; none → FAIL.

Reading of the legs, fixed here so the verdict is mechanical:

- An arm *passes* iff it survives the dev gate AND passes virgin
  legs (i)–(ii) (a PROVISIONAL PASS counts as a pass, recorded as
  such) AND, for the variant arm X8 only, leg (iii): X8's dev
  LL@2.5 ≤ Gate Zero's in at least half the scored dev seasons
  (≥2 of 4). Gate Zero is exempt from (iii) (it is the comparator);
  for Gate Zero, leg (i) reads LL@2.5 ≤ the best baseline's.
- An arm that fails the dev gate is dead: it is not read on the
  virgin window, except that X8's virgin numbers may be computed
  for the record only if Gate Zero is read — no: frozen rule is
  *no virgin read* for a dead arm; its absence from the virgin
  table is itself recorded in the verdict.
- If Gate Zero and X8 both pass, the lower pooled virgin LL@2.5
  ships; a tie goes to Gate Zero (simpler arm). If only one passes,
  it ships. If none passes, K-J1 verdict is FAIL and nothing ships.

## Operational check (required verdict section, design §5c(ii))

The verdict must contain a section assessing pre-match referee
availability honestly: (a) the fraction of completed-match records
carrying a referee identity, overall and by season, from the
extracted referee table; (b) a plain statement of what historical
(completed-match) data can and cannot prove about pre-match
publication of appointments — the warehouse records are post-match
snapshots and contain no publication timestamp, so they cannot by
themselves prove an appointment was public before kickoff; (c) the
operating rule actually shipped: unknown or thin-history referee →
base arm (Gate Zero) for that fixture, no imputation.

## Outputs

- Engine: `league/J1/engine/cards/` (this league's own code:
  referee extraction, model/harness modules, CLI runner).
- Referee table: `league/J1/engine/cards/referee_table.csv`
  (match_id, season, date, kickoff_utc, referee, referee_known) for
  all J1 matches in the warehouse, plus a coverage summary in the
  results files.
- Dev results: `league/J1/engine/cards/results_dev.json` (+ CSV).
- Virgin results: `league/J1/engine/cards/results_virgin.json`.
- Fitted parameters for the virgin fit:
  `league/J1/engine/cards/fitted_params_virgin.json` (HL, K_PRIOR,
  K_REF, r per method, league means and per-team shrunk rates at
  the 2026 cutoff).
- Virgin predictions: `league/J1/predictions/k_j1_virgin_predictions.csv`
  — the shipped arm's predictions (Gate Zero's if nothing ships,
  labelled in the verdict), one row per 2026 match: expected
  home/away/total yellows, FT ladder P(over 1.5 / 2.5 / 3.5 / 4.5),
  the referee fields actually used (referee, n_prior, multiplier,
  fallback flag/reason), and 1H/2H splits via the frozen cards
  constant 0.383 (1H mean = 0.383·FT mean, 2H mean = 0.617·FT mean;
  1H lines 0.5/1.5/2.5, 2H lines 1.5/2.5/3.5, same NB r). Halves are
  presentation only, never fitted (design §7b, F14).
- Verdict: `league/J1/reports/K_J1_VERDICT.md`, including the
  operational-check section above.

Production code and data are untouched. No push. No merge.
