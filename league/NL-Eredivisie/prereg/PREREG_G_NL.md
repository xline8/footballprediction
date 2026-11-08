# Pre-registration — G-NL (Eredivisie goals model)

Frozen: 2026-11-09, before any fitting. Branch `build/nl-eredivisie`.
Design authority: `league/NL-Eredivisie/analysis/MODEL_DESIGN.md` §1 +
shared validation frame; features per `FEATURES.md` (X1 blend pair,
X2 newcomer priors, X3 set-play); evidence per `EDA.md` (F1/F2/F4/F5).
Reference implementation: production Dixon-Coles in `model_v2.py`
(hl = 270), as ported in `league/J1/engine/goals/`.

## Reference architecture (all arms share this unless an arm says otherwise)

- Dixon-Coles fit, copied pattern from `league/J1/engine/goals/dc.py`:
  iterative multiplicative updates, 14 sweeps, damping 0.7, +0.25
  smoothing, home advantage fitted (init 0.28), attack/defence per
  team (init 0), score matrix to MAXG = 10 with the production `tau`
  low-score correction.
- Rho: chosen per fit from the grid (0.0, −0.05, −0.10, −0.15) by
  weighted log-likelihood on goals only, exactly as production.
- Observation (X1): blend 0.5·goals + 0.5·xG. xG exists for every
  match in this corpus, so the goals-only fallback never binds.
  xG = `expected_goals_home/away` in `league/NL-Eredivisie/data/nl_matches.csv`.
- Time decay: w = 0.5 ** ((cutoff − match_date).days / 270), frozen.
  Blend weight 0.5 frozen — no search.
- Fit scope for a target season S: all matches with date strictly
  before the first match date of S (expanding window, season-blocked:
  one fit per target season, whole season predicted from that fit).
- Teams unseen in training start at the league mean (a = d = 0).

## Arms

1. **Gate Zero** — the unmodified reference above. Newcomers start at
   the league mean.
2. **Arm X2** — Gate Zero plus newcomer priors (feature X2, EDA F4).
   A club is a *newcomer* for target season S when it plays in S and
   did not play in this league in the immediately preceding season
   S−1 (team id present in the CSV for S, absent for S−1). For a
   newcomer, at prediction time in season S only:
   - attack: `a += log(max(mu − 0.45, 0.10) / mu)`
   - defence: `d += log((mu + 0.26) / mu)`
   where mu is the decay-weighted mean goals per team per match in
   the training window, and −0.45 / +0.26 are the pooled F4
   magnitudes (GF gap −0.45, GA gap +0.26 per match over the four
   complete transitions 2022/2023–2025/2026). The offset is added to
   the fitted rating (league mean 0 for a first-time club). Clubs
   with no immediately-preceding-season record in either direction
   start at the league mean in every arm.
3. **Arm X3** — Arm X2 plus an open-play/set-play decomposition tilt
   of the xG observation (feature X3, EDA F5), identical in form to
   G-J1's X3 arm: decay-weighted per-team open-play and set-play xG
   for/against means over the training window; multipliers
   `att_mult(t) = sqrt((op_for/L_op)·(sp_for/L_sp))`,
   `def_mult(t) = sqrt((op_against/L_op)·(sp_against/L_sp))`,
   clamped to [0.5, 2.0]; predicted lambdas scaled by
   `sqrt(att_mult · def_mult)` cross-wise; shrinkage exponent 0.5
   frozen; a team with fewer than 8 xG matches in the training
   window gets multiplier 1.0.

## Dev protocol

- Dev period: seasons 2021/2022–2024/2025. Season 2021/2022 is the
  initial training window; evaluation seasons are 2022/2023,
  2023/2024, 2024/2025 under the expanding season-blocked
  walk-forward (pooled dev n = 918).
- Metrics per arm per season and pooled: mean 1X2 log-loss, mean
  RPS (H, D, A), mean OU2.5 log-loss.
- Baselines: climatology — for target season S, the pooled outcome
  rates and OU2.5 over-rate of all seasons strictly before S.
- The dev harness must not read season "2025/2026" or "2026/2027"
  rows at all.

## Virgin protocol

- Virgin window: season "2025/2026" (n = 306, complete). Fit = all
  matches dated before the first 2025/2026 match. Read ONCE, after
  dev results are frozen in the results file.
- Virgin climatology: pooled 2021/2022–2024/2025 outcome rates and
  OU2.5 over-rate.
- Calibration per arm: (i) mean predicted home-win probability minus
  actual home-win rate; (ii) mean predicted P(over 2.5) minus actual
  over-rate. SE = sd(pred_i − y_i)/√n, reported with the difference.

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev 1X2 LL and RPS of an arm must beat climatology, and OU2.5 LL must beat the base-rate baseline, else the arm is dead. Virgin legs — (i) LL leg: arm's virgin 1X2 LL ≤ Gate Zero's AND ≤ climatology's; (ii) calibration leg: |mean predicted − actual| ≤ 1.0pp pooled for home-win rate and for OU2.5 over-rate, SEs reported; a breach within 1 SE of the boundary is recorded PROVISIONAL PASS, beyond it FAIL; (iii) per-season sign check on dev (arm LL ≤ Gate Zero LL in at least half the dev seasons) for the both-pass rule. Both-pass rule: if Gate Zero and a variant both pass all legs, the lower pooled virgin 1X2 LL ships; if only one passes, it ships; if none passes, G-NL verdict is FAIL and nothing ships.

Reading of the legs, fixed here so the verdict is mechanical:

- An arm *passes* iff it survives the dev gate AND passes virgin
  legs (i)–(ii) (a PROVISIONAL PASS counts as a pass, recorded as
  such) AND, for variant arms only, leg (iii). Gate Zero is exempt
  from (iii).
- If several variant arms pass together with Gate Zero, the lower
  pooled virgin 1X2 LL ships; ties go to the simpler arm (Gate Zero
  before X2 before X3).
- If Gate Zero fails its dev gate, the variants are moot in the
  sense of the design's NOT-built clause only if no arm passes dev;
  arms that pass dev are still read on the virgin (the legs above
  govern).

## Outputs

- Engine: `league/NL-Eredivisie/engine/goals/` (this league's own
  code: fit/predict/harness modules + a CLI runner).
- Dev results: `league/NL-Eredivisie/engine/goals/results_dev.json` (+ CSV).
- Virgin results: `league/NL-Eredivisie/engine/goals/results_virgin.json`.
- Fitted parameters for the virgin fit:
  `league/NL-Eredivisie/engine/goals/fitted_params_virgin.json`.
- Virgin predictions: `league/NL-Eredivisie/predictions/g_nl_virgin_predictions.csv`
  — the shipped arm's predictions (Gate Zero's if nothing ships,
  labelled in the verdict), one row per 2025/2026 match, with FT
  lambdas, FT 1X2 / OU (1.5, 2.5, 3.5) / BTTS probabilities, and
  1H/2H lines derived by splitting the same lambdas with the frozen
  NL goals constant 0.444 (1H λ = 0.444·FT λ, 2H λ = 0.556·FT λ;
  1H OU lines 0.5/1.5/2.5, 2H OU lines 1.5/2.5/3.5, same rho and
  score-matrix machinery). Halves are presentation only.
- Verdict: `league/NL-Eredivisie/reports/G_NL_VERDICT.md`.

Production code and data are untouched. No push. No merge.
