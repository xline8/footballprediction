# Pre-registration — K-J2 (J2 cards model)

Frozen: 2026-11-09, before any fitting. Branch `build/k-j2`.
Governed by `league/J1/analysis/MODEL_DESIGN.md` §5 (K-J1/K-J2), the
shared validation frame in its preamble, `FEATURES.md` X5/X8, and
EDA F8/F13. Nothing in this document may be changed after fitting
begins; amendments, if any, are appended as a dated section, never
edited into the frozen text.

## 1. Product scope

- J2 yellow-cards model, **full-time only**. No halves presentation
  of any kind for J2 (MODEL_DESIGN §5; F13: J2 has no per-half
  stats). Primary line **2.5**, secondary line **3.5** (reported,
  not gated).
- Target = unified yellows, `yellow_home + yellow_away` from
  `league/J2/data/j2_matches.csv`. Provenance (PREPROCESSING.md
  rule 6): J2's stats block carries no card keys, so the unified
  columns come from the **event feed** for every J2 match
  (`cards_source='events'`).
- Coverage checked before freezing (this is a data fact, not a
  fit): unified yellows present for **2,318/2,318** rows —
  2021: 462/462 (mean 1.721), 2022: 465/465 (2.056), 2023: 465/465
  (2.660), 2024: 383/383 (2.371), 2025: 383/383 (2.501),
  2026/2027: 160/160 (2.619, excluded from everything). Corpus
  mean 2.275; dev pooled mean 2.195. Reds are never a target
  (FEATURES R12).

## 2. Reference architecture (both arms)

The production cards pattern of `model_cards.py`, copied into
J2's own engine (`league/J2/engine/cards/`) per the per-league
engines decision (MODEL_DESIGN §7b.5):

- Venue-split decayed team ratings: each team carries decayed
  received-cards (`att`) and conceded-cards (`def`) states for
  home and away, plus decayed league home/away means; exponential
  decay half-life **HL = 270 days** and prior shrinkage
  **K_PRIOR = 8 match-equivalents**, both frozen at the production
  values — not tuned.
- Prediction, exactly as production:
  `exp_home = mu_h · (shrunk att_h(home)/mu_h) · (shrunk def_a(away)/mu_h)`,
  mirrored for `exp_away`; total mean `mu = exp_home + exp_away`.
- Count distribution: Negative Binomial, `P(over line)` by the
  production `nb_over` recurrence. The size `r` is **not** the
  production 112.39 (a top-5 tuning quantity); it is estimated
  once, from the dev walk-forward only, by the production
  method-of-moments route around the match-specific means:
  `1/r = Σ[(y − mu)² − mu] / Σ mu²` over scored dev matches,
  clipped to [5, 500] (if the numerator ≤ 0, r = 500). This
  estimation uses dev outcomes only; it happens after the dev
  predictions exist (r does not affect the ratings) and before
  any virgin access. The same dev-estimated `r` is used for the
  virgin predictions and recorded in the fitted params.
- Evaluation is sequential and causal: matches are processed in
  (date, match_id) order, **grouped by date** — all matches on a
  date are predicted from state built only on earlier dates,
  then all are updated. No state fitted on data at or after a
  match's date is ever used for that match.

## 3. Data and evaluation frame

- Input: `league/J2/data/j2_matches.csv` only (plus the warehouse
  JSONs under `data_enrichment/fotmob_jleague/J2/**` for the
  referee table, §4). Season `2026/2027` rows are excluded from
  everything (not dev, not virgin, not training).
- **Dev**: walk-forward expanding, seasons **2021–2024**,
  sequential predict-then-update as in §2, state starting empty
  at the corpus start. February 2021 (11 matches) is the cold
  start: those matches update state but are **excluded from
  scored dev for all arms and baselines** (no prior data exists
  in the corpus). Scored dev n = 1,775 − 11 = 1,764.
- **Virgin**: season **2025** (n=383). Read **once**, only for
  arms that pass the dev gate, after dev results are frozen.
  Evaluated with the same sequential walk-forward, state carried
  over from all matches strictly before each 2025 date (i.e. the
  full 2021–2024 history — the virgin is never trained on
  itself). No parameter, threshold, or design choice may be
  tuned on it. J2's 2025 window is still virgin (G-J2 died at
  its dev gate without reading it) and is protected exactly the
  same way here.
- Team identity is FotMob `team_id` (names are display only).

## 4. Referee work (Arm X8 input)

- Extract the referee for every J2 match from the warehouse
  JSONs at the FEATURES X8 path,
  `content.matchFacts.infoBox.Referee.text`, keyed by match id
  (the JSON filename stem). Build the referee table
  `league/J2/engine/cards/referee_table.csv` with one row per
  match: match_id, season, date, home_team, away_team, referee
  (empty string if the field is empty/missing), referee_present.
  Document the coverage by season in the table's companion
  results and in the verdict. **No other referee source may be
  substituted** — if this field is empty, the referee is unknown
  for that match, full stop.
- The referee table is a data artefact; building it reads no
  yellows outcomes beyond the match ids/dates already in the
  CSV, and it is built for all seasons including 2025 (identity
  is a fixture fact under the FEATURES causality contract — but
  see the virgin rule in §6: the virgin *outcomes* are not read
  until the gate decision).

## 5. Arms

### Gate Zero
The unmodified reference architecture of §2 (feature X5's
ratings side). Nothing else.

### Arm X8 — referee strictness covariate (feature X8)
Identical to Gate Zero except for a multiplicative referee
adjustment applied to the total mean when — and only when — the
appointed referee is known and has enough causal history:

- Referee history: that referee's J2 matches with date strictly
  before the target match's date (same date-grouping rule as §2).
- Minimum history: **8 prior in-league matches** (FEATURES X8).
  Below it, or referee unknown/empty: **Gate Zero fallback** —
  the prediction is exactly Gate Zero's, and the match is
  counted as a fallback in dev and virgin reports.
- Shrunk referee rate (ratio-of-sums, FEATURES causality
  contract): `ref_rate = (Σ yellows in referee's prior matches
  + K_REF · league_mean) / (n_prior + K_REF)` with
  **K_REF = 8** frozen here, where `league_mean` is the decayed
  league total mean (`mu_h + mu_a`) from the Gate Zero state at
  that date.
- Adjustment: `factor = ref_rate / league_mean`, clamped to
  [0.70, 1.40]; `mu_x8 = mu_gate_zero · factor`. Home/away split
  of the adjusted total keeps Gate Zero's proportions. The same
  dev-estimated NB `r` converts `mu_x8` to probabilities.

## 6. Baselines (dev and virgin, same sequential causality)

- **League base rate**: constant P(over 2.5) equal to the
  empirical over-2.5 rate in all J2 matches with date strictly
  before the predicted date, clipped to [0.01, 0.99]. (For the
  secondary line, the same construction at 3.5.)
- **Naive trailing-10** (feature X5): for each team, the mean
  total yellows in its last 10 matches strictly before the date
  (all available matches if fewer than 10, minimum 1; a team
  with no prior match contributes the expanding league mean
  total). `mu_naive = (mean_home + mean_away) / 2`; P(over)
  from a **Poisson** distribution with mean `mu_naive`.

## 7. Metrics

- Binary log-loss at 2.5 (primary) and 3.5 (secondary):
  mean `−[y·ln p + (1−y)·ln(1−p)]`, p clipped to
  [1e-9, 1−1e-9]. Pooled and per season, for both arms and both
  baselines.
- Virgin calibration at 2.5: mean predicted P(over 2.5) vs the
  actual over rate, with
  `SE = sqrt(var(pred)/n + p_act(1−p_act)/n)`.

## 8. Gate legs (verbatim, binding)

Dev gate — pooled dev LL@2.5 beats BOTH baselines (league base rate; naive trailing-10), else arm dead, no virgin read.

Virgin legs — (i) LL@2.5 ≤ Gate Zero's and ≤ best baseline's; (ii) calibration |mean P(over 2.5) − actual| ≤ 1.0pp, SE reported, breach within 1 SE = PROVISIONAL PASS; (iii) dev per-season sign check for both-pass. Both-pass: both → lower pooled virgin LL ships; one → ships; none → FAIL.

Operationalisations, fixed here before fitting:

- Leg (iii): an arm is eligible for the both-pass rule only if
  its dev LL@2.5 beats **both** baselines in at least **3 of
  the 4** scored dev seasons (2021–2024). An arm that passes
  virgin legs (i)–(ii) but fails (iii) may still ship if it is
  the *only* arm passing (i)–(ii); leg (iii) decides
  eligibility only when both arms pass. For Gate Zero itself,
  virgin leg (i) reduces to LL@2.5 ≤ best baseline's.
- Both-pass tie: X8's predictions can coincide with Gate
  Zero's (e.g. if every fixture falls back). If both arms pass
  and their pooled virgin LL@2.5 is equal to within 1e-12, the
  lower-LL rule cannot separate them and **Gate Zero ships** —
  the arm that adds no measured value does not ship.
- A PROVISIONAL PASS on leg (ii) counts as a pass for the
  both-pass rule and is labelled provisional in the verdict.
- If no arm passes the dev gate, the virgin window is **not
  read**: no virgin predictions are generated, season 2025
  stays unburned, and the verdict is FAIL.

## 9. Operational check (binding part of the verdict)

The verdict must contain an honest operational-check section on
pre-match referee availability: what the warehouse data proves
(the per-season coverage of `Referee.text` for J2, and — for
contrast — that the same field is populated for J1, i.e. this is
a J2 publication fact, not a parser artefact), and what it
cannot prove (whether any external source publishes J2 referee
appointments before kickoff — this build checks no external
source and claims nothing about one). The operating rule is the
design's own: **a fixture whose referee is not known falls back
to Gate Zero; referees are never imputed.** If the coverage is
zero, X8 is inactive by construction and the verdict must say
so plainly rather than presenting a Gate Zero clone as a
referee model.

## 10. Deliverables

- Engine: `league/J2/engine/cards/k_j2.py` (Gate Zero + X8 +
  baselines + referee extraction), runnable with the main repo
  `.venv` python, stdlib only.
- Referee table: `league/J2/engine/cards/referee_table.csv`.
- Dev results: `league/J2/engine/cards/dev_results.json`
  (pooled + per-season LL@2.5/@3.5 for both arms and both
  baselines, fallback counts, dev-estimated NB r).
- Fitted params: `league/J2/engine/cards/fitted_params.json`
  (HL, K_PRIOR, K_REF, min history, NB r, final league means,
  training n).
- Virgin predictions (only if an arm passes dev):
  `league/J2/predictions/k_j2_virgin_predictions.csv`,
  full-time only, one row per 2025 match with both arms'
  expected totals and P(over 2.5)/P(over 3.5), the actual total
  yellows, referee and fallback flag.
- Verdict: `league/J2/reports/K_J2_VERDICT.md`, including the
  §9 operational check.
