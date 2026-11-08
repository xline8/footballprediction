# Pre-registration — C-SCOCH (Scotland Championship corners model)

Frozen: 2026-11-10, before any fitting. Branch `build/sco-championship`.
Design authority: `analysis/MODEL_DESIGN.md` (C-SCOCH); features X5,
X9-possession-only; evidence EDA (corners for 0.321 / against
0.480; possession 0.638). Reference: production
`model_corners_v3.py`; sibling analogue
`league/RU-1Division/prereg/PREREG_C_RU1.md` — its shared engine is
carried over verbatim in form (HL = 270 base rates, rolling-5
relative factors clamped [0.6, 1.7], core mean `mu_cs`, NB pmf grid
0..50, per-season gamma/beta/r fitting on prior-season walk-forward
rows only, gamma grid (0.0, 0.15, 0.3, 0.45, 0.6, 0.8), r clamped
[1.02, 5.0], territorial multiplier clamped [0.70, 1.43], min-8 of
last-10 validity rule, date-grouped predict-then-update state).
Phase rule (frozen): all rows are phase `regular`; no phase feature.
Calibration = **predicted − actual** everywhere in this build.

- Target: total corners (stats feed). Primary line **9.5**
  (dev-period over-rate 0.5386, closest to 0.5; the 10.5 over-rate
  is 0.4262). Ladder 8.5 / 9.5 / 10.5 reported, gate at 9.5.
- Arms: **Gate Zero only** — the production pattern with the
  possession-only territorial covariate: beta grid exactly as the
  possession part of PREREG_C_RU1 (poss ∈ ±{0, .0025, .005, .0075,
  .010}). The big-chance term is OMITTED: `big_chance` is absent
  except in the 19 rich 2021/2022 payloads (FEATURES X9). X7 is
  NOT an arm: `touches_opp_box` likewise exists only in those 19.
  No variant arm is registered; the dev gate decides whether the
  single arm lives.
- Training seed 2021/2022; dev evaluation 2022/2023–2024/2025
  (stats rows n = 427; rows without stats are never scored and
  never update state — the 2024/2025 rounds 9–28 outage is skipped
  by this rule). Dev harness must not read 2025/2026 / 2026/2027
  rows.
- Baselines: league base rate (per-season NB from decay-weighted
  pre-season window, as PREREG_C_J1) and naive trailing-10 (X5)
  through the same per-season NB size.
- Virgin: 2025/2026 (stats rows n = 177), read ONCE, only if Gate
  Zero passes the dev gate. Calibration at 9.5 = mean predicted −
  actual, SE = sd(p_i − y_i)/√n.
- Halves: NONE — no period splits exist for corners in this
  league; FT presentation only.

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev LL@9.5 beats BOTH baselines (league base rate; naive trailing-10), else the candidate is dead, no virgin read. Virgin legs — (i) LL@9.5 ≤ best baseline's; (ii) calibration |mean P(over 9.5) − actual| ≤ 1.0pp, SE reported, breach within 1 SE = PROVISIONAL PASS. If Gate Zero passes all legs it ships; if any leg fails, C-SCOCH verdict is FAIL and nothing ships.

Mechanical reading: Gate Zero passes iff it survives the dev gate
AND passes virgin legs (i)–(ii) (PROVISIONAL counts, recorded as
such). Gate Zero dev failure ⇒ FAIL, virgin NOT read.

## Outputs

Engine `engine/corners/`; `results_dev.json` (+ CSV);
`results_virgin.json`; `fitted_params_virgin.json`; on PASS,
`predictions/c_scoch_virgin_predictions.csv` (FT ladder
8.5/9.5/10.5; NO halves columns — FT only). Verdict
`reports/C_SCOCH_VERDICT.md`.
