# Pre-registration — S-NLE (Eerste Divisie shots-on-target model)

Frozen: 2026-11-09, before any fitting. Branch `build/nl-eerste`.
Design authority: `league/NL-EersteDivisie/analysis/MODEL_DESIGN.md`;
features per `FEATURES.md` (X5 base; X4/X6 dropped — no shotmap);
evidence per `EDA.md` (F2). Reference implementation: production
`model_sot.py` v5, as ported in `league/NL-Eredivisie/engine/sot/`.

Scope: predictions-only product. No Eerste Divisie SOT odds or
settlement source exists in-system; expected, not a defect.

## Target and lines

- Target: total SOT = `ShotsOnTarget_home + ShotsOnTarget_away`
  (stats feed; blocked shots excluded). Present for all matches.
- Primary line: **9.5** (dev 2021/2022–2024/2025 mean 9.644,
  over-rate 48.75% — closest to 50%). Ladder: 8.5 / 9.5 / 10.5.
  All gate legs use LL at line 9.5 (binary log-loss, natural log,
  on P(over 9.5)).

## Reference architecture — v5, frozen constants (both arms share)

Copied pattern from `league/NL-Eredivisie/engine/sot/model.py`
(the NL port of production `model_sot.py`), constants unchanged:

- Joint ridge Poisson regression per league: log(mu_home) =
  beta_h + A[home] + D[away], log(mu_away) = beta_a + A[away] +
  D[home]; ridge lambda = 100; exponential decay half-life
  HL = 365 days; lazy refit cadence 7 days; Newton solver, eta
  clipped to [−6, 4], exactly as v5.
- Total-shots component: venue-split decayed ratings (HL 365),
  shrunk to the decayed league mean with prior K = 8; implied SOT
  per team = expected total shots × on-target ratio.
- On-target ratio (Gate Zero form): Beta-Binomial smoothing
  ratio = (S_sot + P·rho) / (S_shots + P), P = 200 pseudo-shots,
  rho = decayed league SOT/shots ratio at that venue.
- Per-team model expectation: exp = 0.5 · regression exp +
  0.5 · implied-shots exp.
- Ensemble: final P(over L) = 0.5 · NB_over(model total) +
  0.5 · NB_over(naive total), naive = trailing-10 team means
  (for/against averaged; league-mean fallback from the regression).
- Line probabilities from Negative Binomial with frozen size
  r = 79.94 (v5 value; not re-estimated here).

## Walk-forward protocol (dev and virgin share it)

Per-match walk-forward, chronological (date, then match_id): state
is updated with a match only **after** that match has been
predicted (predict-then-update). Warm-up: season 2021/2022 matches
update all state but are never scored — the scored dev era is
2022/2023–2024/2025 (n = 1140).

## Arms

1. **Gate Zero (GZ)** — v5 pattern unmodified, as above.
2. **Arm RS (ratio-shrink)** — Gate Zero with exactly one change:
   the BB prior raised from P = 200 to **P = 20,000 pseudo-shots**.

## Baselines (harness, not models)

- **League base rate**: for target season S, P(over 9.5) = the
  over-9.5 rate of all matches in seasons strictly before S
  (constant within S).
- **Naive trailing-10**: the v5 naive total scored through the same
  NB (r = 79.94) — the ensemble's naive term alone.

## Dev protocol

- Scored dev matches: seasons 2022/2023, 2023/2024, 2024/2025
  (n = 1140), per-match walk-forward as above. The dev harness must
  not read season "2025/2026" or "2026/2027" rows at all.
- Metric: mean binary log-loss at line 9.5, per season and pooled,
  per arm and per baseline. Secondary: LL at 8.5/10.5 (reported,
  not gated).

## Virgin protocol

- Virgin window: season "2025/2026" (n = 380), read **ONCE**, only
  for arms that pass the dev gate, and only after dev results are
  frozen. The walk-forward continues from the dev run's end state.
  No parameter is tuned on the virgin window.
- Virgin metrics per arm: LL@9.5; calibration = **actual over-9.5
  rate − mean P(over 9.5)**, with SE = sd(y_i − p_i)/√n reported.

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev LL@9.5 beats BOTH baselines (league base rate; naive trailing-10), else arm dead, no virgin read. Virgin legs — (i) LL@9.5 ≤ Gate Zero's and ≤ best baseline's; (ii) calibration |actual − predicted| ≤ 1.0pp, SE reported, breach within 1 SE = PROVISIONAL PASS; (iii) dev per-season sign check for both-pass. Both-pass: both → lower pooled virgin LL ships; one → ships; none → FAIL.

Reading of the legs, fixed here so the verdict is mechanical:

- The "best baseline" in virgin leg (i) is the lower-LL of the two
  baselines scored on the virgin window.
- Leg (iii): for a variant arm, its dev LL@9.5 ≤ Gate Zero's dev
  LL@9.5 in at least half of the dev seasons (≥ 2 of 3). Gate Zero
  is exempt.
- An arm *passes* iff it survives the dev gate AND passes virgin
  legs (i)–(ii) (PROVISIONAL PASS counts, recorded as such) AND,
  for variant arms, leg (iii).
- Both-pass rule across all passing arms: the lowest pooled virgin
  LL@9.5 ships; ties go to the simpler arm (Gate Zero before RS).
  If no arm passes, S-NLE verdict is FAIL and nothing ships.
- Design NOT-built clause: if Gate Zero fails its own dev gate, the
  variant is moot — verdict FAIL regardless of variant dev numbers,
  and the virgin window is not read.

## Forbidden

Lineup/absence features; trailing conversion/finishing/on-target
form features as standalone covariates (only v5's internal BB ratio
component and its RS arm form above are permitted); half-share
modelling (halves via the frozen constant 0.451 in presentation
only); two-stage generative distributions (V11); xG/xGOT inputs
(none exist); post-match snapshots.

## Outputs

- Engine: `league/NL-EersteDivisie/engine/sot/`.
- Dev results: `engine/sot/results_dev.json` (+ CSV).
- Virgin results: `engine/sot/results_virgin.json`.
- Fitted parameters: `engine/sot/fitted_params_virgin.json`.
- Virgin predictions (shipped arm only, on PASS):
  `league/NL-EersteDivisie/predictions/s_nle_virgin_predictions.csv`
  — one row per 2025/2026 match: match_id, date, teams, actual total
  SOT, exp_sot_home/away/total, FT ladder P(over 8.5/9.5/10.5)
  (ensemble probabilities), and 1H/2H ladders derived
  presentation-only from the same model total via the frozen SOT
  constant 0.451 (NB r = 79.94; 1H lines 3.5/4.5/5.5, 2H lines
  4.5/5.5/6.5). Halves are never fitted.
- Verdict: `league/NL-EersteDivisie/reports/S_NLE_VERDICT.md`.

Production code and data are untouched. No push. No merge.
