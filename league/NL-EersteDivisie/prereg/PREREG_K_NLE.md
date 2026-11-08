# Pre-registration — K-NLE (Eerste Divisie cards model)

Frozen: 2026-11-09, before any fitting. Branch `build/nl-eerste`.
Design authority: `league/NL-EersteDivisie/analysis/MODEL_DESIGN.md`;
feature per `FEATURES.md` X8 (referee yellow rate, trailing —
ADOPTED, coordinator correction: coverage 95.8–100% in scored dev
seasons, strictness split-half r = 0.420, 32 referees ≥ 20 matches;
program precedent adopts at r = 0.378); evidence per `EDA.md`
(F2/F4). Reference implementation: production `model_cards.py`, as
ported in `league/NL-Eredivisie/engine/cards/` — decayed team card
ratings (venue-split attack/defence), shrinkage to the league mean,
Negative Binomial count distribution; referee NOT used in
production.

## Target and data

- Target: total yellows per match = `yellow_home + yellow_away`,
  the **event-unified** columns (events with type == Card and
  card == Yellow only; YellowRed/Red are not yellows), per the
  PREPROCESSING cards-source check: stats-vs-events mismatch on
  10.89% of matches pooled, stats undercounting in five of six
  seasons. Stats columns are retained as cross-check only.
- Dev (2021/2022–2024/2025) mean 3.163 (event-unified). Primary
  line **3.5** (dev over-rate 41.25% at 3.5 vs 61.91% at 2.5 — 3.5
  is the ladder line closest to 50%); ladder 2.5 / 3.5 / 4.5
  reported. Log loss is binary, natural log, on P(over line); all
  gate legs use line 3.5.
- Processing order is chronological by (date, match_id). Every
  prediction uses only matches processed strictly before it; state
  updates happen after prediction. Warm-up: season 2021/2022
  updates state but is never scored; scored dev seasons are
  2022/2023, 2023/2024, 2024/2025 (n = 1140).

## Reference architecture (Gate Zero; both arms share it)

Copied pattern from `league/NL-Eredivisie/engine/cards/model.py`
(the NL port of production `model_cards.py`), constants frozen at
the production values — no search:

- Exponentially decayed rates, half-life **HL = 270 days**: per
  team and venue, yellows for (attack) and yellows conceded
  (defence); decayed league means `mu_h`, `mu_a`.
- Shrinkage to the league mean with prior **K_PRIOR = 8**
  match-equivalents: `shrunk = (s + K·mu) / (w + K)`.
- `exp_home = mu_h · (shrunk att_h(home)/mu_h) · (shrunk def_a(away)/mu_h)`;
  `exp_away` mirrored. Fallback league means before any history are
  the port's (they can only bind in the first warm-up matches).
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
   Referees with no prior in-league matches, and matches whose
   referee text is empty (coverage: 47.4% of warm-up 2021/2022,
   0–4.2% of scored dev seasons, 10.5% of the virgin season), get
   factor 1.0 — fallback to Gate Zero, never imputation.
   Operational condition: if referee appointments are not
   published pre-match in the live pipeline, fixtures fall back to
   Gate Zero — the warehouse build cannot prove live publication.

## Baselines (harness, not models)

- **League base rate**: for target season S, P(over 3.5) = the
  over-3.5 rate of all matches in seasons strictly before S
  (constant within S).
- **Naive trailing-10**: trailing-10 team yellow for/against means
  combined to a match total, scored through the same NB
  (r = 112.39).

## Dev protocol

- Scored dev matches: seasons 2022/2023, 2023/2024, 2024/2025
  (n = 1140). The dev harness must not read "2025/2026" or
  "2026/2027" rows at all.
- Metric: mean binary log-loss at line 3.5, per season and pooled,
  per arm and per baseline.

## Virgin protocol

- Virgin window: season "2025/2026" (n = 380), read **ONCE**, only
  for arms that pass the dev gate, after dev results are frozen.
  The walk-forward continues from the dev run's end state.
- Virgin metrics per arm: LL@3.5; calibration = **actual over-3.5
  rate − mean P(over 3.5)**, SE = sd(y_i − p_i)/√n reported.

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev LL@3.5 beats BOTH baselines (league base rate; naive trailing-10), else arm dead, no virgin read. Virgin legs — (i) LL@3.5 ≤ Gate Zero's and ≤ best baseline's; (ii) calibration |actual − predicted| ≤ 1.0pp, SE reported, breach within 1 SE = PROVISIONAL PASS; (iii) dev per-season sign check for both-pass. Both-pass: both → lower pooled virgin LL ships; one → ships; none → FAIL.

Reading of the legs, fixed here so the verdict is mechanical:

- The "best baseline" in virgin leg (i) is the lower-LL of the two
  baselines scored on the virgin window.
- Leg (iii): for a variant arm, its dev LL@3.5 ≤ Gate Zero's dev
  LL@3.5 in at least half of the dev seasons (≥ 2 of 3). Gate Zero
  is exempt.
- An arm *passes* iff it survives the dev gate AND passes virgin
  legs (i)–(ii) (PROVISIONAL PASS counts, recorded as such) AND,
  for variant arms, leg (iii).
- Both-pass rule: the lowest pooled virgin LL@3.5 ships; ties go
  to the simpler arm (Gate Zero before X8). If no arm passes,
  K-NLE verdict is FAIL and nothing ships.
- Design NOT-built clause: if Gate Zero fails its own dev gate, the
  variant is moot — verdict FAIL regardless of variant dev numbers,
  and the virgin window is not read.

## Forbidden

Red-card modelling as a target; half-share modelling (halves via
the frozen constant 0.326 in presentation only); post-match
snapshots; referee imputation.

## Outputs

- Engine: `league/NL-EersteDivisie/engine/cards/`.
- Dev results: `engine/cards/results_dev.json` (+ CSV).
- Virgin results: `engine/cards/results_virgin.json`.
- Fitted parameters: `engine/cards/fitted_params_virgin.json`.
- Virgin predictions (shipped arm only, on PASS):
  `league/NL-EersteDivisie/predictions/k_nle_virgin_predictions.csv`
  — one row per 2025/2026 match with actual total yellows, expected
  total, FT ladder P(over 2.5/3.5/4.5), and 1H/2H ladders derived
  presentation-only via the frozen yellows constant 0.326 (1H lines
  0.5/1.5/2.5, 2H lines 1.5/2.5/3.5). Halves are never fitted.
- Verdict: `league/NL-EersteDivisie/reports/K_NLE_VERDICT.md`.

Production code and data are untouched. No push. No merge.
