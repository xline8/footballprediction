# Pre-registration — T-AE (AE-ProLeague total shots model)

Frozen: 2026-11-10, before any fitting. Branch `build/ae-proleague`.
Design authority: `analysis/MODEL_DESIGN.md` (T-AE). Reference: the
shots family (v1 pattern / v2 level layer / E9 trailing-r), engine
port pattern: `league/CY-1Division/engine/total_shots/`.

- Target: total shots = `total_shots_home + total_shots_away` (stats
  feed, 100% every season). Primary line **25.5** (dev over-rate
  0.528, n=545). Ladder 24.5/25.5/26.5 reported, gate at 25.5.
- Arms: **A** (v1 pattern: ratings + fitted NB), **B** (v2 level
  layer), **C** (E9: per-team trailing-200 dispersion r), exactly in
  the T-family ported form.
- Warm-up 2021/2022 never scored; awarded matches excluded.
- Dev: scored seasons **2022/2023–2024/2025 (n=545)**. The dev harness
  must not read 2025/2026 or 2026/2027 rows at all.
- Baselines: league base rate (prior-seasons over-25.5 rate); naive
  trailing-10 through the same NB.
- Virgin: 2025/2026 (n=182), read ONCE, only for dev-passing arms.
  Calibration = mean P(over 25.5) − actual rate, SE reported.
  2026/2027 NOT read.

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev LL@25.5 beats BOTH baselines (league base rate; naive trailing-10), else the arm is dead, no virgin read. Virgin legs — (i) LL@25.5 ≤ arm A's AND ≤ best baseline's (arm A: ≤ best baseline's); (ii) calibration |mean P(over 25.5) − actual| ≤ 1.0pp, SE reported, breach within 1 SE = PROVISIONAL PASS; (iii) dev per-season sign check for both-pass (variant dev LL@25.5 ≤ arm A's in ≥2 of 3 dev seasons). Both-pass: all passing → lowest pooled virgin LL ships; one → ships; none → FAIL.

Mechanical reading: an arm passes iff it survives the dev gate AND
passes virgin legs (i)–(ii) (PROVISIONAL counts, recorded as such)
AND, for variants, leg (iii). Ties → simpler arm (A before B before
C). Arm A dev failure ⇒ variants moot, FAIL, virgin NOT read.

## Outputs

Engine `engine/total_shots/`; `results_dev.json`;
`results_virgin.json`; `fitted_params_virgin.json`; on PASS,
`predictions/t_ae_virgin_predictions.csv` (FT ladder; 1H/2H
presentation via frozen total-shots constant 0.4608). Verdict
`reports/T_AE_VERDICT.md`.
