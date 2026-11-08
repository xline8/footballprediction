# Pre-registration — C-UA (Ukraine Premier League corners model)

Frozen: 2026-11-10, before any fitting. Branch `build/ua-premier`.
Design authority: `analysis/MODEL_DESIGN.md` (C-UA); features X5,
X9-as-audited (FEATURES.md). Reference: production
`model_corners_v3.py`; sibling analogue
`league/CN-SuperLeague/prereg/PREREG_C_CN.md` — engine carried in
form (HL = 270 base rates, rolling-5 relative factors clamped
[0.6, 1.7], NB pmf grid 0..50, per-season gamma/beta/r fitting on
prior-season walk-forward rows only, gamma grid
(0.0, 0.15, 0.3, 0.45, 0.6, 0.8), r clamped [1.02, 5.0],
territorial multiplier clamped [0.70, 1.43], min-8 of last-10
validity rule, date-grouped predict-then-update state). Documented
divergence forced by the feed: the territorial multiplier uses
possession ONLY — `big_chance` and `touches_opp_box` are absent
in every payload, so the X7 arm does not exist and the big-chance
term is inactive by missing data. Era restriction: 2022/2023+
only. Stub rule applies. Calibration = actual − predicted.

- Target: total corners (stats feed). Primary line **8.5**
  (scored-dev over-rate ~0.517). Ladder 8.5 / 9.5 / 10.5, gate at
  8.5. FT-only (no halves source).
- Arms: **Gate Zero only** (possession-covariate form above).
- Seed 2022/2023; dev 2023/2024 + 2024/2025 (valid stats n = 462).
  Dev harness must not read 2025/2026 rows.
- Baselines: league base rate (per-season NB from decay-weighted
  pre-season window, as PREREG_C_J1); naive trailing-10 through
  the same per-season NB size.
- Virgin: 2025/2026 (valid stats n = 223), read ONCE, only if
  Gate Zero passes the dev gate.

## GATE LEGS (verbatim, frozen)
Dev gate — pooled dev LL@8.5 beats BOTH baselines, else FAIL,
virgin NOT read. Virgin legs — (i) LL@8.5 ≤ best baseline's;
(ii) calibration |actual − mean P(over 8.5)| ≤ 1.0pp, SE
reported, breach within 1 SE = PROVISIONAL PASS. Gate Zero passes
iff it survives the dev gate AND passes virgin legs (i)–(ii).

## Outputs
Engine `engine/corners/`; `results_dev.json`;
`results_virgin.json`; `fitted_params_virgin.json`; on PASS,
`predictions/c_ua_virgin_predictions.csv` (FT ladder only).
Verdict `reports/C_UA_VERDICT.md`.
