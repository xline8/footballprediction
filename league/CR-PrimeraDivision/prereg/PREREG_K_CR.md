# Pre-registration — K-CR (Costa Rica Primera Division cards model)

Frozen: 2026-11-10, before any fitting. Branch `build/cr-primera-division`.
Design authority: `league/CR-PrimeraDivision/analysis/MODEL_DESIGN.md` §2 (candidate K-CR);
feature per `league/CR-PrimeraDivision/analysis/FEATURES.md` X5 (yellows naive + ratings);
evidence per `league/CR-PrimeraDivision/analysis/EDA.md` F2 (yellows traits), F3 (frozen cards
halves constant 0.379), F4 (reliable cards era), F6 (referee absent).
Reference implementation: production `model_cards.py` — decayed team card ratings (venue-split
attack/defence), shrinkage to the league mean, Negative Binomial count distribution; referee NOT used
in production. Its experiment recipe (`experiments/cards_model/run_cards_experiment.py`) supplies the
baseline definitions and the NB-size estimation formula, unchanged.

## Target and data

- Target: total yellows per match = `yellow_home + yellow_away` in
  `league/CR-PrimeraDivision/data/cr_matches.csv` (Phase 2 columns; `Yellow` + `YellowRed` events,
  `YellowRed` verified paired with an earlier `Yellow` for the same player). Yellows only; straight
  reds are not counted (design §2d). Regular season only; playoffs excluded (card events missing
  2021–2024).
- Reliable era only: seasons 2023/2024 onward (F4). Seasons 2021/2022–2022/2023 are excluded from
  cards entirely — the feed is broken (2021/22: no Yellow events at all) or patchy (Clausura 2022/23:
  10.6% false-zero rate), and false zeros would bias the NB-size estimate.
- Corpus mean on the reliable era (regular): 4.47 yellows/match. Primary line **4.5**
  (over-rate 48.9%), secondary lines **3.5** (63.7%) and **5.5** (32.0%). Log loss is the binary
  log loss (natural log) on P(over line).
- Processing order is chronological by (`date_utc`, `match_id`). Every prediction for a match uses
  only matches processed strictly before it in that order; state updates happen after prediction.

## Reference architecture (Gate Zero; the single arm)

Copied pattern from `model_cards.py`, constants frozen at the production values — no search:

- Exponentially decayed rates, half-life **HL = 270 days**: per team and venue, yellows for (attack)
  and yellows conceded (defence); decayed league means `mu_h`, `mu_a` (home/away yellows per match).
- Shrinkage to the league mean with prior **K_PRIOR = 8** match-equivalents:
  `shrunk = (s + K·mu) / (w + K)`.
- `exp_home = mu_h · (shrunk att_h(home)/mu_h) · (shrunk def_a(away)/mu_h)`;
  `exp_away` mirrored. Fallback league means before any history: `mu_h = 2.15`, `mu_a = 1.95`
  (production constants, kept unchanged as Gate Zero — they can only bind in the first matches of
  the warm-up split, which is never scored; the decayed league means take over within a few matches).
- Match total ~ Negative Binomial(mean = exp_home + exp_away, size r), `P(over L)` from the NB CDF
  exactly as production `nb_over`.

## NB size r — estimation discipline (frozen)

Per method (Gate Zero, base-rate baseline, naive baseline), r is estimated by the production
experiment's method of moments on **causal one-step-ahead residuals of earlier data only**:

    r = Σ μ² / Σ ((y − μ)² − μ),  clipped to [2, 500];
    denominator ≤ 0 → r = 500.

- Dev scoring: r per method is estimated from the 2023/2024 Apertura warm-up split (causal
  predictions only), then frozen for the scored 2023/2024 Clausura split.
- Virgin scoring: r per method is re-estimated from causal predictions over season **2023/2024**
  only, then frozen for season "2024/2025". No virgin outcome enters any r.

## Arms

1. **Gate Zero** — the unmodified reference above. This is the ONLY arm: no referee arm is possible
   (F6 — referee identity absent in 1,328/1,350 matches). The both-pass rule is vacuous and recorded
   as such.

## Baselines (same online pass, identical match set)

- **League base rate**: `mu = mu_h + mu_a`, the decayed league means at the match day (production
  baseline (a); no team information).
- **Naive trailing-10**: production baseline (b) — each team's plain mean yellows for/against over its
  last 10 matches (venues pooled, no shrinkage, no decay); `exp_home = (for(home) + against(away))/2`,
  mirrored for away; falls back to the league means when a team has no history.

## Dev protocol

- Dev period: regular season 2023/2024 only, one chronological online walk-forward pass (expanding;
  state updates after each match). The Apertura split (n = 132) is warm-up: processed, used for the r
  estimation above, never scored. The Clausura split (n = 132) is scored. Pooled dev n = 132.
- Metrics per split and pooled: LL@4.5 (primary), LL@3.5 and LL@5.5 (context), mean predicted
  P(over 4.5) vs actual over rate.
- The dev harness must not read season "2024/2025" (or later) rows at all (neither targets nor histories
  for scored matches). Virgin data is touched only by the separate virgin step, once, after dev results
  are frozen in the results file.

## Virgin protocol

- Virgin window: season "2024/2025", regular only (n = 262). One fresh online pass over
  2023/2024–2024/2025; predictions for 2024/2025 use only earlier matches; r per the discipline above.
  Read ONCE, after dev freezes.
- Calibration per arm at 4.5: mean predicted P(over 4.5) − actual over rate, with
  SE = sd(pred_i − y_i)/√n reported.
- The virgin step also reports the referee-identity coverage of the virgin window (operational check
  evidence — expected 0 known of 262).

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev LL@4.5 beats BOTH baselines (league base rate; naive trailing-10), else arm dead,
no virgin read. Virgin legs — (i) LL@4.5 ≤ best baseline's; (ii) calibration |mean P(over 4.5) − actual|
≤ 1.0pp, SE reported, breach within 1 SE = PROVISIONAL PASS; (iii) dev per-season sign check for
both-pass — VACUOUS for a single-arm candidate (recorded N/A). Both-pass: vacuous (single arm); if
Gate Zero passes all legs it ships; if it fails any leg, K-CR verdict is FAIL and nothing ships.

Reading of the legs, fixed here so the verdict is mechanical:

- The arm *passes* iff it survives the dev gate AND passes virgin legs (i)–(ii) (a PROVISIONAL PASS
  counts as a pass, recorded as such).
- An arm that fails the dev gate is dead: it is not read on the virgin window; its absence from the
  virgin table is itself recorded in the verdict.

## Operational check (required verdict section, design §2c)

The verdict must contain a section assessing pre-match referee availability honestly: (a) the fraction
of completed-match records carrying a referee identity, overall and by season (expected: 0 in 5 of 6
seasons, 22/192 in 2025/2026); (b) a plain statement of what historical (completed-match) data can
and cannot prove about pre-match publication of appointments — the warehouse records are post-match
snapshots and contain no publication timestamp, so they cannot by themselves prove an appointment was
public before kickoff; (c) the operating rule actually shipped: there is no referee arm, so no
fallback is needed — the question is moot for this league, and any future referee arm would require
both identity coverage and a pre-match publication check first.

## Outputs

- Engine: `league/CR-PrimeraDivision/engine/cards/` (this league's own code: model/harness modules,
  CLI runner).
- Dev results: `league/CR-PrimeraDivision/engine/cards/results_dev.json` (+ CSV).
- Virgin results: `league/CR-PrimeraDivision/engine/cards/results_virgin.json`.
- Fitted parameters for the virgin fit:
  `league/CR-PrimeraDivision/engine/cards/fitted_params_virgin.json` (HL, K_PRIOR, r per method,
  league means and per-team shrunk rates at the 2024/2025 cutoff).
- Virgin predictions: `league/CR-PrimeraDivision/predictions/k_cr_virgin_predictions.csv`
  — the shipped arm's predictions (Gate Zero's if nothing ships, labelled in the verdict), one row per
  2024/2025 regular match: expected home/away/total yellows, FT ladder P(over 1.5 / 2.5 / 3.5 / 4.5 / 5.5),
  and 1H/2H splits via the frozen cards constant 0.379 (1H mean = 0.379·FT mean, 2H mean = 0.621·FT mean;
  1H lines 0.5/1.5/2.5, 2H lines 1.5/2.5/3.5, same NB r). Halves are presentation only, never fitted
  (design §4, F3).
- Verdict: `league/CR-PrimeraDivision/reports/K_CR_VERDICT.md`, including the operational-check section
  above.

Production code and data are untouched. No push. No merge.
