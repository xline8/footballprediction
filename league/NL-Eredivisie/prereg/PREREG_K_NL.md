# Pre-registration — K-NL (Eredivisie cards model)

Frozen: 2026-11-09, before any fitting. Branch `build/nl-eredivisie`.
Design authority: `league/NL-Eredivisie/analysis/MODEL_DESIGN.md` §4;
feature per `FEATURES.md` X8 (referee yellow rate, trailing);
evidence per `EDA.md` F8 (referee strictness split-half r = 0.512,
coverage 100%), F3 (frozen cards halves constant 0.333).
Reference implementation: production `model_cards.py`, as ported in
`league/J1/engine/cards/` — decayed team card ratings (venue-split
attack/defence), shrinkage to the league mean, Negative Binomial
count distribution; referee NOT used in production.

## Target and data

- Target: total yellows per match = `yellow_home + yellow_away`
  (unified columns; stats-feed provenance for all 1,638 matches in
  this corpus). Yellows only; reds are not counted (design §4d).
- Corpus mean ≈ 2.94 yellows/match; dev (2021/2022–2024/2025) mean
  2.89. Primary line **2.5** (dev over-rate 55.9%), secondary line
  3.5 (reported, not gated). Log loss is binary, natural log, on
  P(over line).
- Processing order is chronological by (date, match_id). Every
  prediction uses only matches processed strictly before it;
  state updates happen after prediction. Warm-up: season
  2021/2022 updates state but is never scored; scored dev seasons
  are 2022/2023, 2023/2024, 2024/2025 (n = 918).

## Reference architecture (Gate Zero; all arms share it)

Copied pattern from `league/J1/engine/cards/model.py` (the J1 port
of production `model_cards.py`), constants frozen at the
production values — no search:

- Exponentially decayed rates, half-life **HL = 270 days**: per
  team and venue, yellows for (attack) and yellows conceded
  (defence); decayed league means `mu_h`, `mu_a`.
- Shrinkage to the league mean with prior **K_PRIOR = 8**
  match-equivalents: `shrunk = (s + K·mu) / (w + K)`.
- `exp_home = mu_h · (shrunk att_h(home)/mu_h) · (shrunk def_a(away)/mu_h)`;
  `exp_away` mirrored. Fallback league means before any history are
  the J1 port's (they can only bind in the first warm-up matches).
- Match total ~ Negative Binomial(mean = exp_home + exp_away,
  size r = **112.39**, the production frozen value), P(over L)
  from the NB CDF exactly as the port's `nb_over`.

## Arms

1. **Gate Zero (GZ)** — the reference above.
2. **Arm X8 (referee covariate)** — Gate Zero with exactly one
   change: the expected total is multiplied by a referee factor
   built from the appointed referee's trailing in-league record
   (feature X8): the referee's decayed (HL = 270) mean yellows per
   match over matches strictly before kickoff, shrunk toward the
   decayed league mean with prior K = 8 match-equivalents;
   factor = shrunk_ref_mean / league_mean, clamped to [0.8, 1.25].
   Referees with no prior in-league matches get factor 1.0.
   Referee identity from the CSV's `referee` column (warehouse
   coverage 100%). Operational condition (design §4c): if referee
   appointments are not published pre-match in the live pipeline,
   fixtures fall back to Gate Zero — the warehouse build cannot
   test that condition; it is recorded in the verdict.

## Baselines (harness, not models)

- **League base rate**: for target season S, P(over 2.5) = the
  over-2.5 rate of all matches in seasons strictly before S.
- **Naive trailing-10**: trailing-10 team yellow for/against means
  combined to a match total, scored through the same NB
  (r = 112.39).

## Dev protocol

- Scored dev: seasons 2022/2023–2024/2025 (n = 918). The dev
  harness must not read "2025/2026" or "2026/2027" rows at all.
- Metric: mean binary log-loss at line 2.5, per season and pooled,
  per arm and per baseline. Secondary LL@3.5 reported.

## Virgin protocol

- Virgin window: season "2025/2026" (n = 306), read **ONCE**, only
  for arms that pass the dev gate, after dev results are frozen.
  The walk-forward continues from the dev run's end state.
- Virgin metrics per arm: LL@2.5; calibration = mean P(over 2.5) −
  actual over-2.5 rate, SE = sd(p_i − y_i)/√n reported.

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev LL@2.5 beats BOTH baselines (league base rate; naive trailing-10), else arm dead, no virgin read. Virgin legs — (i) LL@2.5 ≤ Gate Zero's and ≤ best baseline's; (ii) calibration |mean P(over 2.5) − actual| ≤ 1.0pp, SE reported, breach within 1 SE = PROVISIONAL PASS; (iii) dev per-season sign check for both-pass. Both-pass: both → lower pooled virgin LL ships; one → ships; none → FAIL.

Reading: leg (iii) = variant's dev LL@2.5 ≤ Gate Zero's in at least
half the dev seasons (≥ 2 of 3); Gate Zero exempt. An arm passes iff
it survives the dev gate AND passes virgin (i)–(ii) (PROVISIONAL
counts, recorded as such) AND, for the variant, (iii). Both-pass
across passing arms: lowest pooled virgin LL@2.5 ships; ties go to
Gate Zero. If no arm passes, K-NL verdict is FAIL, nothing ships.

## Forbidden

Red-card modelling as a target; referee imputation (a referee with
no history is factor 1.0, never a guessed identity); half-share
card modelling (halves via the frozen constant 0.333 in
presentation only).

## Outputs

- Engine: `league/NL-Eredivisie/engine/cards/`.
- Dev results: `league/NL-Eredivisie/engine/cards/results_dev.json` (+ CSV).
- Virgin results: `league/NL-Eredivisie/engine/cards/results_virgin.json`.
- Fitted parameters: `league/NL-Eredivisie/engine/cards/fitted_params_virgin.json`.
- Virgin predictions:
  `league/NL-Eredivisie/predictions/k_nl_virgin_predictions.csv` —
  the shipped arm's predictions (Gate Zero's if nothing ships,
  labelled in the verdict): match_id, date, teams, referee, actual
  total yellows, exp_yellows_total, FT ladder P(over 2.5/3.5), and
  1H/2H ladders derived presentation-only via the frozen cards
  constant 0.333 from the same expected total and NB machinery.
- Verdict: `league/NL-Eredivisie/reports/K_NL_VERDICT.md`.

Production code and data are untouched. No push. No merge.
