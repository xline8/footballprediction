# Pre-registration — G-UA (Ukraine Premier League goals model)

Frozen: 2026-11-10, before any fitting. Branch `build/ua-premier`.
Design authority: `analysis/MODEL_DESIGN.md` (G-UA); features X1
goals-only form + SHRINK substitute (FEATURES.md). Reference:
production Dixon-Coles in `model_v2.py` (class `DC`), hl = 270;
sibling analogue `league/CN-SuperLeague/prereg/PREREG_G_CN.md`.
Era restriction (frozen, war-era rule): fits use **2022/2023+
only** — 2021/2022 was terminated after round 18 (invasion) and is
excluded from seed, dev and virgin alike. Phase rule: all rows
ordinary (single-group format). Calibration = actual − predicted.

## Reference architecture (all arms share unless an arm says otherwise)
- Dixon-Coles fit, production pattern: iterative multiplicative
  updates, 14 sweeps, damping 0.7, +0.25 smoothing, home advantage
  fitted (init 0.28), attack/defence per team (init 0), MAXG = 10,
  production tau correction. Rho per fit from grid
  (0.0, −0.05, −0.10, −0.15) by weighted goals log-likelihood.
- Observation: goals only (no xG exists in this corpus).
- Time decay w = 0.5 ** ((cutoff − match_date).days / 270), frozen.
- Fit scope for season S: all UA matches (2022/2023+ era) strictly
  before the first match date of S (expanding, season-blocked).
  Teams keyed on FotMob ids. Unseen teams start at a = d = 0.

## Arms
1. **Gate Zero** — the unmodified reference above.
2. **Arm SHRINK** (sanctioned G-J2-lesson arm) — Gate Zero plus, at
   prediction time only: a team with fewer than 6 prior in-league
   matches in the training window has ratings shrunk toward the
   league mean: a *= n/6, d *= n/6 (n = prior match count; n = 0
   identical to Gate Zero's unseen rule). Nothing else changes.

## Dev / virgin protocol
- Seed = 2022/2023; dev evaluation 2023/2024 + 2024/2025 (pooled
  n = 480), season-blocked walk-forward. The dev harness must not
  read 2025/2026 rows. Baselines: climatology (pooled outcome +
  OU2.5 rates of era seasons strictly before S).
- Virgin = 2025/2026 (n = 240, last complete season), read ONCE,
  only for arms passing the dev gate. Fit = all era matches before
  the first 2025/2026 match date. 2026/2027 is reserved
  confirmatory and is NOT read in this build.

## GATE LEGS (verbatim, frozen)
Dev gate — pooled dev 1X2 LL and RPS must beat climatology, and
OU2.5 LL must beat the base-rate baseline, else the arm is dead.
Virgin legs — (i) LL leg: arm's virgin 1X2 LL ≤ Gate Zero's AND ≤
climatology's; (ii) calibration leg: |actual − mean predicted|
≤ 1.0pp pooled for home-win rate and for OU2.5 over-rate, SEs
reported; breach within 1 SE = PROVISIONAL PASS, beyond = FAIL;
(iii) per-season sign check on dev (arm LL ≤ Gate Zero LL in at
least half the dev seasons) for the both-pass rule. Both-pass:
lower pooled virgin 1X2 LL ships; one passes → it ships; none →
FAIL, nothing ships. Ties → Gate Zero. Gate Zero dev failure ⇒
variants moot, FAIL, virgin NOT read.

## Outputs
Engine `engine/goals/`; `results_dev.json`; `results_virgin.json`;
`fitted_params_virgin.json`; on PASS,
`predictions/g_ua_virgin_predictions.csv` (1H/2H presentation via
frozen goals constant 0.4441). Verdict `reports/G_UA_VERDICT.md`.
