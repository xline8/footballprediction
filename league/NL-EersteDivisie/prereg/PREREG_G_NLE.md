# Pre-registration — G-NLE (Eerste Divisie goals model)

Frozen: 2026-11-09, before any fitting. Branch `build/nl-eerste`.
Design authority: `league/NL-EersteDivisie/analysis/MODEL_DESIGN.md`;
features per `FEATURES.md` (X2 relegated-club prior adopted; X1/X3
dropped — no xG in this corpus); evidence per `EDA.md` (F1/F2/F5).
Reference implementation: production Dixon-Coles in `model_v2.py`,
as ported in `league/NL-Eredivisie/engine/goals/` (dc.py), with the
documented goals-only fallback (the blend's xG half never exists
here), plus the SHRINK arm form from `league/DE-3Liga/engine/goals/`.

## Reference architecture (all arms share unless an arm says otherwise)

- Dixon-Coles fit, pattern copied from
  `league/NL-Eredivisie/engine/goals/dc.py`: iterative multiplicative
  updates, 14 sweeps, damping 0.7, +0.25 smoothing, home advantage
  fitted (init 0.28), attack/defence per team (init 0), score matrix
  to MAXG = 10 with the production `tau` low-score correction.
- Rho: per fit from the grid (0.0, −0.05, −0.10, −0.15) by weighted
  log-likelihood on goals only, exactly as the reference.
- Observation: **goals only** (no xG key exists in this corpus).
- Time decay: w = 0.5 ** ((cutoff − match_date).days / 270), frozen.
- Fit scope for target season S: all matches with date strictly
  before the first match date of S (expanding, season-blocked: one
  fit per target season, whole season predicted from that fit).
- Teams unseen in training start at the league mean (a = d = 0).

## Arms

1. **Gate Zero** — the unmodified reference above.
2. **Arm SHRINK** — Gate Zero plus the frozen <6 prior-match rating
   shrink (DE-3Liga form): at prediction time each team's attack
   and defence ratings are multiplied by min(1, n_prior/6), where
   n_prior = that team's match count in the training window.
3. **Arm X2** — Gate Zero plus relegated-club priors (feature X2,
   EDA F5 as corrected). A club is a *mover* for target season S
   when it plays in S, did not play in this league in S−1, and
   played in the Eredivisie in S−1 (verified for every observed
   transition; any entrant not meeting the Eredivisie condition
   starts at the league mean in every arm). For a mover, at
   prediction time in season S only:
   - attack: `a += log((mu + 0.419) / mu)`
   - defence: `d += log((mu − 0.199) / mu)`
   where mu is the decay-weighted mean goals per team per match in
   the training window, and +0.419 / −0.199 are the pooled
   coordinator-verified F5 magnitudes (GF gap +0.419, GA gap −0.199
   per team-match, four complete transitions, n = 456 entrant
   team-matches). The offset is added to the fitted rating.

## Dev protocol

- Dev period: seasons 2021/2022–2024/2025. 2021/2022 is the initial
  training window; evaluation seasons are 2022/2023, 2023/2024,
  2024/2025 under the expanding season-blocked walk-forward
  (pooled dev n = 1140).
- Metrics per arm per season and pooled: mean 1X2 log-loss, mean
  RPS (H, D, A), mean OU2.5 log-loss.
- Baselines: climatology — for target season S, the pooled outcome
  rates and OU2.5 over-rate of all seasons strictly before S.
- The dev harness must not read season "2025/2026" or "2026/2027"
  rows at all.

## Virgin protocol

- Virgin window: season "2025/2026" (n = 380, complete). Fit = all
  matches dated before the first 2025/2026 match. Read ONCE, after
  dev results are frozen, only for arms that pass the dev gate.
- Virgin climatology: pooled 2021/2022–2024/2025 outcome rates and
  OU2.5 over-rate.
- Calibration per arm, **actual − predicted**: (i) actual home-win
  rate minus mean predicted home-win probability; (ii) actual
  over-2.5 rate minus mean predicted P(over 2.5).
  SE = sd(y_i − p_i)/√n, reported with the difference.

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev 1X2 LL and RPS of an arm must beat climatology, and OU2.5 LL must beat the base-rate baseline, else the arm is dead. Virgin legs — (i) LL leg: arm's virgin 1X2 LL ≤ Gate Zero's AND ≤ climatology's; (ii) calibration leg: |actual − predicted| ≤ 1.0pp pooled for home-win rate and for OU2.5 over-rate, SEs reported; a breach within 1 SE of the boundary is recorded PROVISIONAL PASS, beyond it FAIL; (iii) per-season sign check on dev (arm LL ≤ Gate Zero LL in at least half the dev seasons) for the both-pass rule. Both-pass rule: if Gate Zero and a variant both pass all legs, the lower pooled virgin 1X2 LL ships; if only one passes, it ships; if none passes, G-NLE verdict is FAIL and nothing ships.

Reading of the legs, fixed here so the verdict is mechanical:

- An arm *passes* iff it survives the dev gate AND passes virgin
  legs (i)–(ii) (a PROVISIONAL PASS counts as a pass, recorded as
  such) AND, for variant arms only, leg (iii). Gate Zero is exempt
  from (iii).
- If several variant arms pass together with Gate Zero, the lower
  pooled virgin 1X2 LL ships; ties go to the simpler arm (Gate Zero
  before SHRINK before X2).
- If no arm passes dev, the virgin is NOT read and the verdict
  records that.

## Outputs

- Engine: `league/NL-EersteDivisie/engine/goals/` (fit/predict/
  harness modules + CLI runner, README).
- Dev results: `engine/goals/results_dev.json` (+ CSV).
- Virgin results: `engine/goals/results_virgin.json`.
- Fitted parameters (virgin fit, shipped arm):
  `engine/goals/fitted_params_virgin.json`.
- Virgin predictions (shipped arm only, on PASS):
  `league/NL-EersteDivisie/predictions/g_nle_virgin_predictions.csv`,
  one row per 2025/2026 match, with FT lambdas, FT 1X2 / OU
  (1.5, 2.5, 3.5) / BTTS probabilities, and 1H/2H lines derived by
  splitting the same lambdas with the frozen goals constant 0.451
  (presentation only, never fitted).
- Verdict: `league/NL-EersteDivisie/reports/G_NLE_VERDICT.md`.

Production code and data are untouched. No push. No merge.
