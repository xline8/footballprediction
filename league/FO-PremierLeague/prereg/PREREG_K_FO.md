# Pre-registration — K-FO (Faroe Islands Premier League cards model)

Frozen: 2026-11-10, before any fitting. Branch `build/fo-premier-league`.
Design authority: `league/FO-PremierLeague/analysis/MODEL_DESIGN.md`
(candidate K-FO) + shared validation frame; features per
`league/FO-PremierLeague/analysis/FEATURES.md` (X5 trailing yellows
adopted; X8 referee DROPPED — referee text empty 810/810);
evidence per `league/FO-PremierLeague/analysis/EDA.md` (F2 yellows
traits split-half r = 0.869 for / 0.851 against, F5 cards levels,
F14 frozen cards halves constant 0.348).
Reference implementation: production `model_cards.py` — decayed
team card ratings (venue-split attack/defence), shrinkage to the
league mean, Negative Binomial count distribution; referee NOT used
in production. Its experiment recipe supplies the baseline
definitions and the NB-size estimation formula, unchanged.

## Target and data

- Target: total yellows per match = `yellow_home + yellow_away` in
  `league/FO-PremierLeague/data/fo_premier_league_matches.csv`
  (unified yellows: Yellow + YellowRed events from the event feed;
  straight Red events are NOT counted, per program rule R12).
  The awarded match 3822183 is excluded from every pass.
- Corpus mean ≈ 3.94 yellows/match (played matches). Primary line
  **3.5**, secondary line **4.5**. Log loss is the binary log loss
  (natural log) on P(over line).
- Processing order is chronological by (`date`, `match_id`).
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

Per method (Gate Zero, SHRINK, base-rate baseline, naive baseline), r is
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
2. **Arm SHRINK** — Gate Zero with K_PRIOR = **16** instead of 8
   (double prior weight toward the league mean). No other change.
   This is the pre-registered shrinkage-sensitivity arm for a
   10-team league with ~2-club churn per season.

No referee arm exists: the appointed referee's identity is empty in
all 810 payloads (`infoBox.Referee.text` == ""), so feature X8 is
DROPPED at the data level and no referee covariate can be defined.
The verdict must contain an operational-check section recording
referee-identity coverage 0/810 and stating plainly that no referee
arm can be added without a new preregistration and a new data source.

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
  (pooled n = 539).
- Metrics per arm/baseline per season and pooled: LL@3.5 (primary),
  LL@4.5 (context), mean predicted P(over 3.5) vs actual over rate.
- The dev harness must not read season "2026" rows at all. Virgin
  data is touched only by the separate virgin step, once, after dev
  results are frozen in the results file.

## Virgin protocol

- Virgin window: season "2026" (n = 135, complete). One fresh online
  pass over 2021–2026; predictions for 2026 use only earlier
  matches; r per the discipline above. Read ONCE, after dev freezes.
- Calibration per arm at 3.5: mean predicted P(over 3.5) − actual
  over rate, with SE = sd(pred_i − y_i)/√n reported.

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev LL@3.5 beats BOTH baselines (league base rate; naive trailing-10), else arm dead, no virgin read. Virgin legs — (i) LL@3.5 ≤ Gate Zero's and ≤ best baseline's; (ii) calibration |mean P(over 3.5) − actual| ≤ 1.0pp, SE reported, breach within 1 SE = PROVISIONAL PASS; (iii) dev per-season sign check for both-pass. Both-pass: both → lower pooled virgin LL ships; one → ships; none → FAIL.

Reading of the legs, fixed here so the verdict is mechanical:

- An arm *passes* iff it survives the dev gate AND passes virgin
  legs (i)–(ii) (a PROVISIONAL PASS counts as a pass, recorded as
  such) AND, for the variant arm SHRINK only, leg (iii): SHRINK's dev
  LL@3.5 ≤ Gate Zero's in at least half the scored dev seasons
  (≥2 of 4). Gate Zero is exempt from (iii) (it is the comparator);
  for Gate Zero, leg (i) reads LL@3.5 ≤ the best baseline's.
- An arm that fails the dev gate is dead: it is not read on the
  virgin window. Its absence from the virgin table is itself recorded
  in the verdict.
- If Gate Zero and SHRINK both pass, the lower pooled virgin LL@3.5
  ships; a tie goes to Gate Zero (simpler arm). If only one passes,
  it ships. If none passes, K-FO verdict is FAIL and nothing ships.

## Outputs

- Engine: `league/FO-PremierLeague/engine/cards/` (this league's own
  code: model/harness modules + a CLI runner).
- Dev results: `league/FO-PremierLeague/engine/cards/results_dev.json`
  (+ `results_dev.csv`, one row per scored dev match with per-arm
  probabilities — summary-only rows are not acceptable).
- Virgin results: `league/FO-PremierLeague/engine/cards/results_virgin.json`
  (or a `{"virgin_read": false, ...}` marker when virgin is not read).
- Fitted parameters for the virgin fit:
  `league/FO-PremierLeague/engine/cards/fitted_params_virgin.json`
  (HL, K_PRIOR, r per method, league means and per-team shrunk rates
  at the 2026 cutoff).
- Virgin predictions: `league/FO-PremierLeague/predictions/k_fo_virgin_predictions.csv`
  — the shipped arm's predictions (Gate Zero's if nothing ships,
  labelled in the verdict), one row per 2026 match: expected
  home/away/total yellows, FT ladder P(over 1.5 / 2.5 / 3.5 / 4.5),
  and 1H/2H splits via the frozen cards constant 0.348 (1H mean =
  0.348·FT mean, 2H mean = 0.652·FT mean; 1H lines 0.5/1.5/2.5,
  2H lines 1.5/2.5/3.5, same NB r). Halves are presentation only,
  never fitted.
- Verdict: `league/FO-PremierLeague/reports/K_FO_VERDICT.md`,
  including the operational-check section above.

Production code and data are untouched. No push. No merge.
