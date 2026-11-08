# Pre-registration — G-IE (Ireland Premier Division goals model)

Frozen: 2026-11-10, before any fitting. Branch `build/ie-premier`.
Design authority: `league/IE-PremierDivision/analysis/MODEL_DESIGN.md`
(G-IE); features per `analysis/FEATURES.md` (X1 goals-only, X5);
evidence per `analysis/EDA.md` / `eda_numbers.json`.
Reference: production Dixon-Coles in `model_v2.py` (class `DC`),
hl = 270; SCO analogue `league/SCO-Premiership/prereg/PREREG_G_SCO.md`
with the deviations frozen below.

## Reference architecture (all arms share unless an arm says otherwise)

- Dixon-Coles fit, copied pattern from production `model_v2.py`:
  iterative multiplicative updates, 14 sweeps, damping 0.7, +0.25
  smoothing, home advantage fitted (init 0.28), attack/defence per
  team (init 0), score matrix MAXG = 10, production `tau` correction.
- Rho per fit from grid (0.0, −0.05, −0.10, −0.15) by weighted
  log-likelihood on goals only, as production.
- Observation: **GOALS ONLY**. IE xG exists only in 2025–2026 (one dev
  season plus the virgin); the production blend cannot be
  dev-validated here, so the xG columns are ignored by frozen design
  (FEATURES X1). This is the many-precedent goals-only case.
- Time decay w = 0.5 ** ((cutoff − match_date).days / 270), frozen.
- Fit scope for target season S: all IE matches dated strictly before
  the first match date of S (expanding, season-blocked).
- Teams unseen in training start at the league mean (a = d = 0).

## Arms

1. **Gate Zero** — the unmodified reference above.
2. **Arm SHRINK** (sanctioned G-J2-lesson arm) — Gate Zero plus
   exactly one change at prediction time: for a team with fewer than
   6 prior in-league matches in the training window, its fitted
   attack and defence ratings are shrunk toward the league mean:
   `a *= n/6`, `d *= n/6` where n = its prior in-league match count
   (n = 0 ⇒ a = d = 0, identical to Gate Zero's unseen rule; the arm
   bites exactly for teams with 1–5 prior matches — the season-opener
   failure mode; IE has ~1 promoted club per season). Nothing else
   changes.

## Dev protocol

- Training seed = 2021; evaluation seasons 2022, 2023, 2024, 2025
  (pooled n = 720) under the season-blocked walk-forward.
- Metrics per arm per season and pooled: mean 1X2 LL, mean RPS
  (H, D, A), mean OU2.5 LL. Baselines: climatology — for target
  season S, pooled outcome rates + OU2.5 over-rate of all seasons
  strictly before S.
- The dev harness must not read 2026 rows at all.

## Virgin protocol

- Virgin = 2026 (n = 180, complete, ended 2026-10-30), read ONCE,
  only for arms passing the dev gate, after dev results are frozen.
  Fit = all matches dated before the first 2026 match (2021–2025).
- Virgin climatology: pooled 2021–2025 outcome rates and OU2.5
  over-rate.
- Calibration per arm: (i) mean predicted home-win probability minus
  actual home-win rate; (ii) mean predicted P(over 2.5) minus actual
  over-rate. SE = sd(pred_i − y_i)/√n.

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev 1X2 LL and RPS of an arm must beat climatology, and OU2.5 LL must beat the base-rate baseline, else the arm is dead. Virgin legs — (i) LL leg: arm's virgin 1X2 LL ≤ Gate Zero's AND ≤ climatology's; (ii) calibration leg: |mean predicted − actual| ≤ 1.0pp pooled for home-win rate and for OU2.5 over-rate, SEs reported; a breach within 1 SE of the boundary is recorded PROVISIONAL PASS, beyond it FAIL; (iii) per-season sign check on dev (arm LL ≤ Gate Zero LL in at least half the dev seasons) for the both-pass rule. Both-pass rule: if Gate Zero and a variant both pass all legs, the lower pooled virgin 1X2 LL ships; if only one passes, it ships; if none passes, G-IE verdict is FAIL and nothing ships.

Mechanical reading: an arm *passes* iff it survives the dev gate AND
passes virgin legs (i)–(ii) (a PROVISIONAL PASS counts as a pass,
recorded as such) AND, for variant arms only, leg (iii) — SHRINK dev
1X2 LL ≤ Gate Zero's in ≥2 of the 4 dev seasons. Gate Zero is exempt
from (iii). Ties go to the simpler arm (Gate Zero before SHRINK).
If Gate Zero fails its dev gate, the variant is moot, verdict FAIL,
virgin NOT read.

## Outputs

- Engine: `league/IE-PremierDivision/engine/goals/` (fit/predict/
  harness + CLI runner, this league's own code).
- Dev results: `engine/goals/results_dev.json` (+ per-match CSV).
- Fitted parameters for the virgin fit:
  `engine/goals/fitted_params_virgin.json`.
- Virgin predictions: `league/IE-PremierDivision/predictions/g_ie_virgin_predictions.csv`
  — the shipped arm's predictions (Gate Zero's if nothing ships,
  labelled in the verdict), one row per 2026 match, with FT lambdas,
  FT 1X2 / OU (1.5, 2.5, 3.5) / BTTS probabilities, and 1H/2H lines
  derived by splitting the same lambdas with the frozen IE goals
  constant 0.4439 (1H λ = 0.4439·FT λ, 2H λ = 0.5561·FT λ; 1H OU lines
  0.5/1.5/2.5, 2H OU lines 1.5/2.5/3.5, same rho and score-matrix
  machinery). Halves are presentation only, never fitted.
- Verdict: `reports/G_IE_VERDICT.md`.

Production code and data are untouched. No push. No merge.
