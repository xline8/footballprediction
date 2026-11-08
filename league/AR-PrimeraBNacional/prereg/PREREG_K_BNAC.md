# Pre-registration — K-BNAC (Primera B Nacional cards model)

Frozen: 2026-11-10, before any fitting. Branch `build/ar-primera-b`.
Design authority: `league/AR-PrimeraBNacional/analysis/MODEL_DESIGN.md` §3;
feature per `FEATURES.md` X8 (referee yellow rate, trailing);
evidence per `EDA.md` F8 (referee strictness split-half r = 0.525,
47 referees with ≥8 matches, 2023+ era; coverage 0% in 2021,
88.6% in 2022, 94.8% / 94.9% / 97.2% in 2023–2025),
F3 (frozen yellows halves constant 0.390091).
Reference implementation: production `model_cards.py`, as ported in
`league/J1/engine/cards/` — decayed team card ratings (venue-split
attack/defence), shrinkage to the league mean, Negative Binomial
count distribution; referee NOT used in production.
S-BNAC / C-BNAC / T-BNAC are NOT preregistered (not buildable —
MODEL_DESIGN §4).

## Target and data

- Target: total yellows per match = `yellow_home + yellow_away`
  (unified columns; **event-feed provenance, `card='Yellow'` only** —
  YellowRed/Red are reds, not yellows). Yellows only; reds are not
  counted.
- The cards target exists ONLY from 2023: the 2021–2022 event feed
  carries zero `card='Yellow'` events, so those seasons' card
  columns are NaN (feed absent, never 0) and are excluded from the
  cards corpus entirely.
- Corpus mean 2023–2025 ≈ 4.76 yellows/match; scored dev (blocks
  2024–2025) mean 4.6784, over-4.5 rate 51.05%. Primary line **4.5**
  (nearest the median), secondary line 5.5 (reported, not gated;
  scored-dev over-rate 33.06%). Log loss is binary, natural log, on
  P(over line).
- Processing order is chronological by (date, match_id). Every
  prediction uses only matches processed strictly before it;
  state updates happen after prediction. Warm-up: block 2023
  updates state but is never scored; scored dev blocks are 2024,
  2025 (n = 1,334).

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
   coverage 94.8% / 94.9% / 97.2% in 2023 / 2024 / 2025; 2021 has
   none and is outside the cards corpus). Operational condition
   (design §3): if referee appointments are not published pre-match
   in the live pipeline, fixtures fall back to Gate Zero — the
   warehouse build cannot test that condition; it is recorded in
   the verdict.

## Baselines (harness, not models)

- **League base rate**: for target block S, P(over 4.5) = the
  over-4.5 rate of all matches in blocks strictly before S (within
  the cards corpus, i.e. from 2023).
- **Naive trailing-10**: trailing-10 team yellow for/against means
  combined to a match total, scored through the same NB
  (r = 112.39).

## Dev protocol

- Scored dev: blocks 2024 – 2025 (n = 1,334). The dev harness must
  not read block "2026" rows at all.
- Metric: mean binary log-loss at line 4.5, per block and pooled,
  per arm and per baseline. Secondary LL@5.5 reported.

## Virgin protocol

- Virgin window: block "2026" (n = 648), read **ONCE**, only for
  arms that pass the dev gate, after dev results are frozen.
  The walk-forward continues from the dev run's end state.
- **Frozen rule: if Gate Zero fails its dev gate, the variants are
  moot and the virgin is NOT read — even if a variant arm passes
  dev.**
- Virgin metrics per arm: LL@4.5; calibration = mean P(over 4.5) −
  actual over-4.5 rate, SE = sd(p_i − y_i)/√n reported.

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev LL@4.5 beats BOTH baselines (league base rate; naive trailing-10), else arm dead, no virgin read. Virgin legs — (i) LL@4.5 ≤ Gate Zero's and ≤ best baseline's; (ii) calibration |mean P(over 4.5) − actual| ≤ 1.0pp, SE reported, breach within 1 SE = PROVISIONAL PASS; (iii) dev per-block sign check for both-pass. Both-pass: both → lower pooled virgin LL ships; one → ships; none → FAIL.

Reading: leg (iii) = variant's dev LL@4.5 ≤ Gate Zero's in at least
half the dev blocks (≥ 1 of 2); Gate Zero exempt. An arm passes iff
it survives the dev gate AND passes virgin (i)–(ii) (PROVISIONAL
counts, recorded as such) AND, for the variant, (iii). Both-pass
across passing arms: lowest pooled virgin LL@4.5 ships; ties go to
Gate Zero. If no arm passes, K-BNAC verdict is FAIL, nothing ships.

## Forbidden

Red-card modelling as a target; referee imputation (a referee with
no history is factor 1.0, never a guessed identity); half-share
card modelling (halves via the frozen constant 0.390091 in
presentation only); using 2021–2022 rows for cards in any form
(their Yellow feed does not exist).

## Outputs

- Engine: `league/AR-PrimeraBNacional/engine/cards/`.
- Dev results: `league/AR-PrimeraBNacional/engine/cards/results_dev.json` (+ CSV).
- Virgin results: `league/AR-PrimeraBNacional/engine/cards/results_virgin.json`.
- Fitted parameters: `league/AR-PrimeraBNacional/engine/cards/fitted_params_virgin.json`.
- Virgin predictions:
  `league/AR-PrimeraBNacional/predictions/k_bnac_virgin_predictions.csv` —
  the shipped arm's predictions (Gate Zero's if nothing ships,
  labelled in the verdict): match_id, date, teams, referee, actual
  total yellows, exp_yellows_total, FT ladder P(over 4.5/3.5), and
  1H/2H ladders derived presentation-only via the frozen yellows
  constant 0.390091 from the same expected total and NB machinery.
- Verdict: `league/AR-PrimeraBNacional/reports/K_BNAC_VERDICT.md`.

Production code and data are untouched. No push. No merge.
