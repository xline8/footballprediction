# Pre-registration — G-CR (Costa Rica Primera Division goals model)

Frozen: 2026-11-10, before any fitting. Branch `build/cr-primera-division`.
Design authority: `league/CR-PrimeraDivision/analysis/MODEL_DESIGN.md` §1 (candidate G-CR);
features per `league/CR-PrimeraDivision/analysis/FEATURES.md` (X1 goals-only, X5 goals naive);
evidence per `league/CR-PrimeraDivision/analysis/EDA.md` (F1/F2/F3/F5).
Reference implementation: production Dixon-Coles in `model_v2.py` (class `DC`, `probs`),
production config `v2_config.json` (hl = 270); closest in-program copy `league/J1/engine/goals/`.

## Reference architecture (the single arm, Gate Zero)

- Dixon-Coles fit, copied pattern from production `model_v2.py`: iterative multiplicative updates,
  14 sweeps, damping 0.7, +0.25 smoothing, home advantage `h` fitted (init 0.28), attack `a` and
  defence `d` per team (init 0), score matrix to MAXG = 10 with the production `tau` low-score correction.
- Rho: chosen per fit from the grid (0.0, −0.05, −0.10, −0.15) by weighted log-likelihood on goals only,
  exactly as production.
- Observation (X1): goals-only throughout — this league has no xG anywhere, so every match enters
  goals-only (the reference blend's documented fallback; blend weight 0.5 is moot with no xG).
- Time decay: weight w = 0.5 ** ((cutoff − match_date).days / 270). Half-life 270 days is the production
  value, frozen — no search.
- Fit scope for a target season S: all CR regular-season matches with date strictly before the first
  match date of S (expanding window, season-blocked: one fit per target season, whole season predicted
  from that fit). Playoffs are never in scope.
- Teams unseen in training start at the league mean (a = d = 0). Each target season has exactly one
  such team (the promoted side, EDA F5); no team ever has 1–9 prior matches, so no thin-history variant
  exists or is needed.

## Arms

1. **Gate Zero** — the unmodified reference above. This is the ONLY arm: no cross-tier prior exists
   (no second tier in the warehouse — FEATURES X2), no thin-history variant is applicable (F5), no
   set-play / xG variant is possible (no xG). The both-pass rule is vacuous and recorded as such.

## Dev protocol

- Dev period: regular seasons 2021/2022–2023/2024. Season 2021/2022 is the initial training window;
  evaluation seasons are 2022/2023 (n = 228 regular) and 2023/2024 (n = 264 regular) under the
  expanding season-blocked walk-forward above. Pooled dev n = 492.
- Metrics per season and pooled: mean 1X2 log-loss (natural log), mean RPS (outcomes ordered H, D, A;
  RPS = 0.5 · Σ_k (Σ_{j≤k} p_j − Σ_{j≤k} y_j)²), mean OU2.5 log-loss (binary, on P(over 2.5)).
- Baselines: climatology — for target season S, the pooled outcome rates (home win / draw / away win)
  and OU2.5 over-rate of all CR regular seasons strictly before S. The same climatology probabilities
  score LL, RPS and OU LL for that season.
- The dev harness must not read season "2024/2025" (or later) rows at all. Virgin data is touched only
  by the separate virgin step, once, after dev results are frozen in the results file.

## Virgin protocol

- Virgin window: season "2024/2025", regular only (n = 262). Fit = all CR regular matches dated before
  the first 2024/2025 match (seasons 2021/2022–2023/2024). Read ONCE, after dev freezes.
- Virgin climatology: pooled 2021/2022–2023/2024 outcome rates and OU2.5 over-rate.
- Calibration per arm: (i) mean predicted home-win probability minus actual home-win rate;
  (ii) mean predicted P(over 2.5) minus actual over-rate. Standard error of each difference:
  SE = sd(pred_i − y_i) / √n over the 262 matches, reported with the difference.

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev 1X2 LL and RPS of the arm must beat climatology, and OU2.5 LL must beat the
base-rate baseline, else the arm is dead. Virgin legs — (i) LL leg: the arm's virgin 1X2 LL ≤
climatology's; (ii) calibration leg: |mean predicted − actual| ≤ 1.0pp pooled for home-win rate and for
OU2.5 over-rate, SEs reported; a breach within 1 SE of the boundary is recorded PROVISIONAL PASS, beyond
it FAIL; (iii) per-season sign check on dev (arm LL ≤ Gate Zero LL in at least half the dev seasons)
for the both-pass rule — VACUOUS for a single-arm candidate (Gate Zero is the only arm; recorded N/A).
Both-pass rule: vacuous (single arm). If Gate Zero passes all legs it ships; if it fails any leg,
G-CR verdict is FAIL and nothing ships.

Reading of the legs, fixed here so the verdict is mechanical:

- The arm *passes* iff it survives the dev gate AND passes virgin legs (i)–(ii) (a PROVISIONAL PASS
  counts as a pass, recorded as such).
- An arm that fails the dev gate is dead: it is not read on the virgin window; its absence from the
  virgin table is itself recorded in the verdict.

## Outputs

- Engine: `league/CR-PrimeraDivision/engine/goals/` (this league's own code: fit/predict/harness
  modules + a CLI runner).
- Dev results: `league/CR-PrimeraDivision/engine/goals/results_dev.json` (+ CSV).
- Fitted parameters for the virgin fit:
  `league/CR-PrimeraDivision/engine/goals/fitted_params_virgin.json`.
- Virgin predictions: `league/CR-PrimeraDivision/predictions/g_cr_virgin_predictions.csv`
  — the shipped arm's predictions (Gate Zero's if nothing ships, labelled in the verdict), one row per
  2024/2025 regular match, with FT lambdas, FT 1X2 / OU (1.5, 2.5, 3.5) / BTTS probabilities, and
  1H/2H lines derived by splitting the same lambdas with the frozen CR goals constant 0.460
  (1H λ = 0.460·FT λ, 2H λ = 0.540·FT λ; 1H OU lines 0.5/1.5/2.5, 2H OU lines 1.5/2.5/3.5, same rho
  and score-matrix machinery). Halves are presentation only, never fitted (design §4).
- Verdict: `league/CR-PrimeraDivision/reports/G_CR_VERDICT.md`.

Production code and data are untouched. No push. No merge.
