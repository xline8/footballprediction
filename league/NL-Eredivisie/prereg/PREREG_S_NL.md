# Pre-registration — S-NL (Eredivisie shots-on-target model)

Frozen: 2026-11-09, before any fitting. Branch `build/nl-eredivisie`.
Design authority: `league/NL-Eredivisie/analysis/MODEL_DESIGN.md` §2;
features per `FEATURES.md` (X5 base; X4 quality input; X6 xGOT
era-guarded; §2 ratio component); evidence per `EDA.md` (F6/F7/F12).
Reference implementation: production `model_sot.py` v5, as ported in
`league/J1/engine/sot/`.

Scope: predictions-only product. There is no Eredivisie SOT odds or
settlement source in-system; that is expected, not a defect.

## Target and lines

- Target: total SOT = `ShotsOnTarget_home + ShotsOnTarget_away`
  (stats feed; blocked shots excluded). Present for all matches.
- Primary line: **9.5** (dev 2021/2022–2024/2025 mean 9.61,
  over-rate 49.3% — nearest the dev median). Ladder: 8.5 / 9.5 /
  10.5. All gate legs use LL at line 9.5 (binary log-loss, natural
  log, on P(over 9.5)).

## Reference architecture — v5, frozen constants (all arms share)

Copied pattern from `league/J1/engine/sot/model.py` (the J1 port of
production `model_sot.py`), constants unchanged (no search):

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
2022/2023–2024/2025 (n = 918).

## Arms

1. **Gate Zero (GZ)** — v5 pattern unmodified, as above.
2. **Arm RS (ratio-shrink)** — Gate Zero with exactly one change:
   the BB prior raised from P = 200 to **P = 20,000 pseudo-shots**.
   (Tests how much of F6's measured team on-target-rate signal,
   r = 0.581, survives inside this architecture.)
3. **Arm X4 (xG/shot quality input)** — Gate Zero with exactly one
   change, *in addition to* the raw total-shots signal: the BB
   on-target ratio is replaced, per team and venue, by
   `ratio_X4 = rho_venue · (q_team / q_league)`, clamped to
   [0.15, 0.50], where `q_team` = Σ sm_xg / Σ sm_shots over the
   team's trailing 25 matches (any venue, strictly pre-match) with
   shotmap aggregates (regulation shots only); minimum 8 such
   matches, else the Gate Zero BB ratio for that team-venue;
   `q_league` = the same ratio of sums over all matches strictly
   before the predicted match; `rho_venue` = the decayed league
   SOT/shots ratio at that venue.
4. **Arm X6 (xGOT, era-guarded)** — Arm X4 as its base, plus the
   attacking xGOT-per-shot trait (X6, F7) under this frozen
   composition rule:
   - Era guard (NL): only matches in seasons **2024/2025 onward**
     (date ≥ 2024-08-01) ever contribute xGOT sums. No earlier
     xGOT value is read anywhere in this arm.
   - `g_t` = Σ sm_xgot / Σ sm_xgot_n over team t's trailing 25
     era-valid matches (strictly pre-match, sm_xgot_n > 0);
     `g_L` = the same ratio of sums over all era-valid matches
     strictly before the predicted match. Minimum 8 era-valid
     matches for the team, else the trait is inactive for it.
   - Multiplier per team: `mult_t = clamp(1 + 0.5·(g_t/g_L − 1),
     0.85, 1.15)`, attacking side only.
   - Composition: model per-team expectations become exp_h·mult_home
     and exp_a·mult_away; the naive ensemble term is unchanged.
     Outside the era / without data, X6 ≡ X4 exactly.

## Baselines (harness, not models)

- **League base rate**: for target season S, P(over 9.5) = the
  over-9.5 rate of all matches in seasons strictly before S
  (constant within S).
- **Naive trailing-10**: the v5 naive total scored through the same
  NB (r = 79.94) — the ensemble's naive term alone.

## Dev protocol

- Scored dev matches: seasons 2022/2023, 2023/2024, 2024/2025
  (n = 918), per-match walk-forward as above. The dev harness must
  not read season "2025/2026" or "2026/2027" rows at all.
- Metric: mean binary log-loss at line 9.5, per season and pooled,
  per arm and per baseline. Secondary: LL at 8.5/10.5 (reported,
  not gated).
- **X6 dev judging (frozen exception)**: X6's dev gate is judged on
  its era folds only — dev matches dated ≥ 2024-08-01 (season
  2024/2025) — against both baselines computed on that same subset.
  Its full-dev numbers are reported for the record.

## Virgin protocol

- Virgin window: season "2025/2026" (n = 306), read **ONCE**, only
  for arms that pass the dev gate, and only after dev results are
  frozen. The walk-forward continues from the dev run's end state.
  No parameter is tuned on the virgin window.
- Virgin metrics per arm: LL@9.5; calibration = mean P(over 9.5) −
  actual over-9.5 rate, with SE = sd(p_i − y_i)/√n reported.

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev LL@9.5 beats BOTH baselines (league base rate; naive trailing-10), else arm dead, no virgin read (X6 judged on its era folds for this leg). Virgin legs — (i) LL@9.5 ≤ Gate Zero's and ≤ best baseline's; (ii) calibration |mean P(over 9.5) − actual| ≤ 1.0pp, SE reported, breach within 1 SE = PROVISIONAL PASS; (iii) dev per-season sign check for both-pass. Both-pass: both → lower pooled virgin LL ships; one → ships; none → FAIL.

Reading of the legs, fixed here so the verdict is mechanical:

- The "best baseline" in virgin leg (i) is the lower-LL of the two
  baselines scored on the virgin window. For X6, virgin leg (i)'s
  comparison to Gate Zero is as written (all arms are read on the
  full virgin window; the era restriction applies to the dev leg
  only).
- Leg (iii): for a variant arm, its dev LL@9.5 ≤ Gate Zero's dev
  LL@9.5 in at least half of the dev seasons (≥ 2 of 3; for X6,
  judged on its era fold: its era-fold LL ≤ Gate Zero's LL on the
  same era subset). Gate Zero is exempt.
- An arm *passes* iff it survives the dev gate AND passes virgin
  legs (i)–(ii) (PROVISIONAL PASS counts, recorded as such) AND,
  for variant arms, leg (iii).
- Both-pass rule across all passing arms: the lowest pooled virgin
  LL@9.5 ships; ties go to the simpler arm (Gate Zero before RS
  before X4 before X6). If no arm passes, S-NL verdict is FAIL and
  nothing ships.
- Design NOT-built clause: if Gate Zero fails its own dev gate, the
  variants are moot — verdict FAIL regardless of variant dev
  numbers, and the virgin window is not read.

## Forbidden

Lineup/absence features (F10); trailing conversion/finishing/
on-target-rate form features as standalone covariates (R2–R4 —
only v5's internal BB ratio component and its RS/X4 arm forms above
are permitted); half-share modelling (halves via the frozen
constant 0.446 in presentation only); two-stage generative
distributions (V11); defensive xGOT (R5); post-match snapshots.

## Outputs

- Engine: `league/NL-Eredivisie/engine/sot/`.
- Dev results: `league/NL-Eredivisie/engine/sot/results_dev.json` (+ CSV).
- Virgin results: `league/NL-Eredivisie/engine/sot/results_virgin.json`.
- Fitted parameters: `league/NL-Eredivisie/engine/sot/fitted_params_virgin.json`.
- Virgin predictions: `league/NL-Eredivisie/predictions/s_nl_virgin_predictions.csv`
  — the shipped arm's predictions (Gate Zero's if nothing ships,
  labelled in the verdict), one row per 2025/2026 match: match_id,
  date, teams, actual total SOT, exp_sot_home/away/total, FT ladder
  P(over 8.5/9.5/10.5) (ensemble probabilities), and 1H/2H ladders
  derived presentation-only from the same model total via the
  frozen SOT constant 0.446 (NB r = 79.94; 1H lines 3.5/4.5/5.5,
  2H lines 4.5/5.5/6.5). Halves are never fitted.
- Verdict: `league/NL-Eredivisie/reports/S_NL_VERDICT.md`.

Production code and data are untouched. No push. No merge.
