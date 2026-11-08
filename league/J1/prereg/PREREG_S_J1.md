# Pre-registration — S-J1 (J1 shots-on-target model)

Frozen: 2026-11-09, before any fitting. Branch `build/s-j1`.
Design authority: `league/J1/analysis/MODEL_DESIGN.md` §3 (candidate
S-J1) + shared validation frame + §7b; features per
`league/J1/analysis/FEATURES.md` (X5 base; X4 quality input; X6 xGOT
era-guarded; §2 ratio component); evidence per
`league/J1/analysis/EDA.md` (F6/F7/F13). Reference implementation:
production `model_sot.py` v5.

Scope: predictions-only product. There is no J.League SOT odds or
settlement source in-system; that is expected, not a defect.

## Target and lines

- Target: total SOT = `ShotsOnTarget_home + ShotsOnTarget_away` in
  `league/J1/data/j1_matches.csv` (stats feed; blocked shots excluded).
- Primary line: **8.5** (pooled stats-era mean ≈ 8.08). Ladder:
  7.5 / 8.5 / 9.5. All gate legs use LL at line 8.5 (binary log-loss,
  natural log, on P(over 8.5)).

## Reference architecture — v5, frozen constants (all arms share)

Copied pattern from `model_sot.py`, constants unchanged (no search):

- Joint ridge Poisson regression per league: log(mu_home) =
  beta_h + A[home] + D[away], log(mu_away) = beta_a + A[away] +
  D[home]; ridge lambda = 100; exponential sample decay half-life
  HL = 365 days; lazy refit cadence 7 days (first prediction request
  on/after the scheduled day refits from matches strictly before that
  day); Newton solver, eta clipped to [−6, 4], exactly as v5.
- Total-shots component: venue-split decayed ratings (HL 365),
  shrunk to the decayed league mean with prior K = 8
  match-equivalents; implied SOT per team = expected total shots ×
  on-target ratio.
- On-target ratio (Gate Zero form): Beta-Binomial smoothing
  ratio = (S_sot + P·rho) / (S_shots + P), P = 200 pseudo-shots,
  rho = decayed league SOT/shots ratio at that venue (v5 BB).
- Per-team model expectation: exp = 0.5 · regression exp +
  0.5 · implied-shots exp.
- Ensemble: final P(over L) = 0.5 · NB_over(model total) +
  0.5 · NB_over(naive total), naive = plain trailing-10 team means
  (for/against averaged, v5 `NaiveTracker`; league-mean fallback
  from the regression when a team has no history).
- Line probabilities from Negative Binomial with frozen size
  r = 79.94 (v5 value; not re-estimated on J1).

## Walk-forward protocol (dev and virgin share it)

Per-match walk-forward, chronological (date, then match_id):
state is updated with a match only **after** that match has been
predicted (predict-then-update). State warm-up: season 2021 matches
update all state (SOT/shots targets exist there) but are never
scored — the scored dev era is the stats era 2022–2025, because the
shotmap-derived inputs (X4/X6) and xG exist only from 2022
(F13). Team indices for the regression span all teams in the data
(indexing only, as in v5).

## Arms

1. **Gate Zero (GZ)** — v5 pattern unmodified, as above.
2. **Arm RS (ratio-shrink)** — Gate Zero with exactly one change:
   the Beta-Binomial prior in the on-target ratio is raised from
   P = 200 to **P = 20,000 pseudo-shots** (100× v5), shrinking each
   team's ratio to (near) the decayed league constant rho at its
   venue. Everything else identical. (Tests F6: team SOT-rate trait
   is NOISE in J1, split-half r = 0.06; FEATURES §2/R4.)
3. **Arm X4 (xG/shot quality input)** — Gate Zero with exactly one
   change, **in addition to** the raw total-shots signal (the
   design's "in place of / in addition to" choice is frozen to
   *in addition to*): the BB on-target ratio is replaced, per team
   and venue, by a quality-adjusted ratio
   `ratio_X4 = rho_venue · (q_team / q_league)`, clamped to
   [0.15, 0.50], where:
   - `q_team` = Σ sm_xg / Σ sm_shots over the team's trailing 25
     matches (any venue, strictly pre-match) that carry shotmap
     aggregates (`sm_xg_*`, `sm_shots_*` from the match CSV,
     regulation shots only per Phase 2); ratio of sums (X4
     definition); minimum 8 such matches, else the arm falls back
     to the Gate Zero BB ratio for that team-venue;
   - `q_league` = Σ sm_xg / Σ sm_shots over all matches strictly
     before the predicted match (expanding, ratio of sums);
   - `rho_venue` = the same decayed league SOT/shots ratio v5 uses.
   The expected-shots ratings, regression, ensemble and NB are
   unchanged.
4. **Arm X6 (xGOT, era-guarded)** — Arm X4 as its base, plus the
   attacking xGOT-per-shot trait (X6, F7), under this frozen
   composition rule:
   - Era guard: only matches dated **2025-01-01 or later** ever
     contribute xGOT sums. No pre-2025 xGOT value is read anywhere
     in this arm (pre-2025 the field is populated only for on-target
     shots — a different quantity).
   - For team t at prediction time: `g_t` = Σ sm_xgot / Σ sm_xgot_n
     over t's trailing 25 era-valid matches (strictly pre-match,
     sm_xgot_n > 0); league era value `g_L` = the same ratio of
     sums over all era-valid matches strictly before the predicted
     match. Minimum 8 era-valid matches for the team, else the
     trait is inactive for that team.
   - Multiplier per team: `mult_t = clamp(1 + 0.5·(g_t/g_L − 1),
     0.85, 1.15)`, attacking side only (a team's own multiplier
     scales its own expected SOT; the defensive side is excluded,
     F7/R5).
   - Composition: model per-team expectations become
     exp_h·mult_home and exp_a·mult_away; the model total entering
     the ensemble's NB term is their sum. The naive ensemble term
     is unchanged. A match dated before 2025-01-01, or lacking an
     active trait for a team, uses the X4 value for that team — so
     outside the era / without data, X6 ≡ X4 exactly.

## Baselines (harness, not models)

- **League base rate**: for target season S, P(over 8.5) = the
  over-8.5 rate of all J1 matches in seasons strictly before S
  (constant within S), scored as a constant probability.
- **Naive trailing-10**: the v5 naive total (trailing-10 team
  for/against means, league-mean fallback) scored through the same
  NB (r = 79.94) — i.e. the ensemble's naive term alone.

## Dev protocol

- Scored dev matches: seasons 2022, 2023, 2024, 2025 (n = 1,372),
  per-match walk-forward as above. The dev harness must not read
  season "2026" or "2026/2027" rows at all.
- Metric: mean binary log-loss at line 8.5, per season and pooled,
  per arm and per baseline. Secondary: LL at 7.5/9.5 (reported, not
  gated).
- **X6 dev judging (frozen exception)**: X6's dev gate is judged on
  its era folds only — the subset of dev matches dated ≥ 2025-01-01
  (season 2025) — against both baselines computed on that same
  subset. Its full-dev numbers are reported for the record.

## Virgin protocol

- Virgin window: season "2026" (n = 200), read **ONCE**, only for
  arms that pass the dev gate, and only after dev results are
  frozen in the results file. The walk-forward continues from the
  dev run's end state (all matches before 2026 scored in order;
  2026 matches predict-then-update among themselves). No parameter
  is tuned on the virgin window.
- Virgin metrics per arm: LL@8.5; calibration = mean P(over 8.5) −
  actual over-8.5 rate, with SE = sd(p_i − y_i)/√n reported.

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev LL@8.5 beats BOTH baselines (league base rate; naive trailing-10), else arm dead, no virgin read (X6 judged on its era folds for this leg). Virgin legs — (i) LL@8.5 ≤ Gate Zero's and ≤ best baseline's; (ii) calibration |mean P(over 8.5) − actual| ≤ 1.0pp, SE reported, breach within 1 SE = PROVISIONAL PASS; (iii) dev per-season sign check for both-pass. Both-pass: both → lower pooled virgin LL ships; one → ships; none → FAIL.

Reading of the legs, fixed here so the verdict is mechanical:

- The "best baseline" in virgin leg (i) is the lower-LL of the two
  baselines scored on the virgin window. For X6, virgin leg (i)'s
  comparison to Gate Zero is as written (all arms are read on the
  full virgin window; the era restriction applies to the dev leg
  only, per the verbatim text).
- Leg (iii), dev per-season sign check: for a variant arm, its dev
  LL@8.5 ≤ Gate Zero's dev LL@8.5 in at least half of the dev
  seasons (≥ 2 of 4; for X6, judged on its era fold: its era-fold
  LL ≤ Gate Zero's LL on the same era subset). Gate Zero is exempt
  (it is the comparator). Leg (iii) is required for a variant to
  ship under the both-pass rule.
- An arm *passes* iff it survives the dev gate AND passes virgin
  legs (i)–(ii) (a PROVISIONAL PASS counts as a pass, recorded as
  such) AND, for variant arms, leg (iii).
- Both-pass rule across all passing arms: the lowest pooled virgin
  LL@8.5 ships; ties go to the simpler arm (Gate Zero before RS
  before X4 before X6). If no arm passes, S-J1 verdict is FAIL and
  nothing ships.
- Design §3 NOT-built clause: if Gate Zero fails its own dev gate,
  the variants are moot — verdict FAIL regardless of variant dev
  numbers, and the virgin window is not read.

## Forbidden (design §3d / §7 — none may enter any arm)

Lineup/absence features (F10 null replicated); trailing
conversion/finishing/on-target-rate form features (standalone
trailing on-target rate as a covariate is R4 — only v5's internal
BB ratio component and its RS/X4 arm forms above are permitted);
half-share modelling (halves via the frozen constant 0.448 in
presentation only); two-stage generative distributions (V11);
defensive xGOT (R5); post-match snapshot features.

## Outputs

- Engine: `league/J1/engine/sot/` (this league's own code:
  model/harness modules + a CLI runner).
- Dev results: `league/J1/engine/sot/results_dev.json` (+ CSV).
- Virgin results: `league/J1/engine/sot/results_virgin.json`.
- Fitted parameters (final state after the virgin window):
  `league/J1/engine/sot/fitted_params_virgin.json`.
- Virgin predictions: `league/J1/predictions/s_j1_virgin_predictions.csv`
  — the shipped arm's predictions (Gate Zero's if nothing ships,
  labelled in the verdict), one row per 2026 match: match_id, date,
  teams, actual total SOT, exp_sot_home/away/total (model
  expectations of the labelled arm), FT ladder P(over 7.5/8.5/9.5)
  (ensemble probabilities), and 1H/2H ladders derived presentation-
  only from the same model total via the frozen SOT constant
  0.448: 1H mean = 0.448 · exp_total, 2H mean = 0.552 · exp_total,
  each scored with NB r = 79.94 at lines 1H 2.5/3.5/4.5 and
  2H 3.5/4.5/5.5. Halves are never fitted.
- Verdict: `league/J1/reports/S_J1_VERDICT.md`.

Production code and data are untouched. No push. No merge.
