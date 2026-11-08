# Pre-registration — G-FO (Faroe Islands Premier League goals model)

Frozen: 2026-11-10, before any fitting. Branch `build/fo-premier-league`.
Design authority: `league/FO-PremierLeague/analysis/MODEL_DESIGN.md`
(candidate G-FO) + shared validation frame; features per
`league/FO-PremierLeague/analysis/FEATURES.md` (X1 goals-only; X2–X9
dropped); evidence per `league/FO-PremierLeague/analysis/EDA.md`
(F1 levels/drift incl. the low-scoring 2026, F2 team-trait
reliabilities GF r=0.876 / GA r=0.928, F3 halves constant 0.441,
F4 churn with no feeder tier).
Reference implementation: production Dixon-Coles in `model_v2.py`
(class `DC`, `probs`), production config `v2_config.json` (hl = 270).

## Reference architecture (all arms share this unless an arm says otherwise)

- Dixon-Coles fit, copied pattern from production `model_v2.py`:
  iterative multiplicative updates, 14 sweeps, damping 0.7, +0.25
  smoothing, home advantage `h` fitted (init 0.28), attack `a` and
  defence `d` per team (init 0), score matrix to MAXG = 10 with the
  production `tau` low-score correction.
- Rho: chosen per fit from the grid (0.0, −0.05, −0.10, −0.15) by
  weighted log-likelihood on goals only, exactly as production.
- Observation (X1): goals only — there is no xG anywhere in this
  corpus (stats 0/810, shotmap 0/810), so the blend's goals-only
  fallback is the whole observation, not an exception.
- Time decay: weight w = 0.5 ** ((cutoff − match_date).days / 270).
  Half-life 270 days is the production value, frozen — no search.
- Fit scope for a target season S: all FO-PremierLeague played
  matches with date strictly before the first match date of S
  (expanding window, season-blocked: one fit per target season,
  whole season predicted from that fit). The awarded match 3822183
  (2022-09-04, official 0-3 AW vs played 3-1) is excluded from every
  fit and every scored set.
- Teams unseen in training start at the league mean (a = d = 0).

## Arms

1. **Gate Zero** — the unmodified reference above.
2. **Arm SHRINK** — Gate Zero plus a uniform rating shrinkage: after
   the fit, every team's fitted attack and defence ratings are
   multiplied by **0.85** toward the league mean (a = d = 0); home
   advantage `h` is untouched. This is the pre-registered answer to
   the G-J2 post-mortem (unmodified DC gives extreme lambdas to
   thin-history teams): FO-PremierLeague turns over ~2 clubs every
   season and returnees re-enter with stale, decayed history. The
   factor 0.85 is frozen — no search, no re-estimation.

## Dev protocol

- Dev period: seasons 2021–2025. Season 2021 is the initial training
  window; evaluation seasons are 2022, 2023, 2024, 2025 under the
  expanding season-blocked walk-forward above. Pooled dev = the four
  evaluation seasons combined (n = 539 played matches: 134 + 135 +
  135 + 135; the awarded match is excluded from the 2022 count).
- Metrics per arm per season and pooled: mean 1X2 log-loss (natural
  log), mean RPS (outcomes ordered H, D, A;
  RPS = 0.5 · Σ_k (Σ_{j≤k} p_j − Σ_{j≤k} y_j)²), mean OU2.5 log-loss
  (binary, on P(over 2.5)).
- Baselines: climatology — for target season S, the pooled outcome
  rates (home win / draw / away win) and OU2.5 over-rate of all
  FO-PremierLeague played seasons strictly before S. The same
  climatology probabilities score LL, RPS and OU LL for that season.
- The dev harness must not read season "2026" rows at all. Virgin
  data is touched only by the separate virgin step, once, after dev
  results are frozen in the results file.

## Virgin protocol

- Virgin window: season "2026" (n = 135, complete). Fit = all
  FO-PremierLeague played matches dated before the first 2026 match
  (seasons 2021–2025). Read ONCE, after dev freezes.
- Virgin climatology: pooled 2021–2025 outcome rates and OU2.5
  over-rate.
- Calibration per arm: (i) mean predicted home-win probability minus
  actual home-win rate; (ii) mean predicted P(over 2.5) minus actual
  over-rate. Standard error of each difference:
  SE = sd(pred_i − y_i) / √n over the 135 matches, reported with the
  difference.

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev 1X2 LL and RPS of an arm must beat climatology, and OU2.5 LL must beat the base-rate baseline, else the arm is dead. Virgin legs — (i) LL leg: arm's virgin 1X2 LL ≤ Gate Zero's AND ≤ climatology's; (ii) calibration leg: |mean predicted − actual| ≤ 1.0pp pooled for home-win rate and for OU2.5 over-rate, SEs reported; a breach within 1 SE of the boundary is recorded PROVISIONAL PASS, beyond it FAIL; (iii) per-season sign check on dev (arm LL ≤ Gate Zero LL in at least half the dev seasons) for the both-pass rule. Both-pass rule: if Gate Zero and a variant both pass all legs, the lower pooled virgin 1X2 LL ships; if only one passes, it ships; if none passes, G-FO verdict is FAIL and nothing ships.

Reading of the legs, fixed here so the verdict is mechanical:

- An arm *passes* iff it survives the dev gate AND passes virgin
  legs (i)–(ii) (a PROVISIONAL PASS counts as a pass, recorded as
  such) AND, for the variant arm SHRINK only, leg (iii). Gate Zero is
  exempt from (iii) (it is the comparator).
- If Gate Zero and SHRINK both pass, the both-pass rule's "lower
  pooled virgin 1X2 LL ships" applies; ties go to the simpler arm
  (Gate Zero before SHRINK).

## Outputs

- Engine: `league/FO-PremierLeague/engine/goals/` (this league's own
  code: fit/predict/harness modules + a CLI runner).
- Dev results: `league/FO-PremierLeague/engine/goals/results_dev.json`
  (+ `results_dev.csv`, one row per scored dev match with per-arm
  probabilities — summary-only rows are not acceptable).
- Fitted parameters for the virgin fit:
  `league/FO-PremierLeague/engine/goals/fitted_params_virgin.json`.
- Virgin predictions: `league/FO-PremierLeague/predictions/g_fo_virgin_predictions.csv`
  — the shipped arm's predictions (Gate Zero's if nothing ships,
  labelled in the verdict), one row per 2026 match, with FT lambdas,
  FT 1X2 / OU (1.5, 2.5, 3.5) / BTTS probabilities, and 1H/2H lines
  derived by splitting the same lambdas with the frozen FO goals
  constant 0.441 (1H λ = 0.441·FT λ, 2H λ = 0.559·FT λ; 1H OU lines
  0.5/1.5/2.5, 2H OU lines 1.5/2.5/3.5, same rho and score-matrix
  machinery). Halves are presentation only, never fitted.
- Virgin results marker: `league/FO-PremierLeague/engine/goals/results_virgin.json`
  (`{"virgin_read": false, ...}` when virgin is not read).
- Verdict: `league/FO-PremierLeague/reports/G_FO_VERDICT.md`.

Production code and data are untouched. No push. No merge.
