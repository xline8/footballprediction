# Pre-registration — C-FI (FI-Veikkausliiga corners model)

Frozen: 2026-11-10, before any fitting. Branch `build/fi-veikkausliiga`.
Design authority: `analysis/MODEL_DESIGN.md` (C-FI); features X5, X9 (partial);
evidence F2/F5. Reference: production `model_corners_v3.py` as frozen in
`PREREG_C_J1.md` / `PREREG_C_SE2.md` (HL = 270 base rates, rolling-5 relative
factors clamped [0.6, 1.7], NB pmf grid 0..50, per-season gamma/beta/r fitting
on prior-season walk-forward rows only, gamma grid (0.0, 0.15, 0.3, 0.45, 0.6, 0.8),
r clamped [1.02, 5.0], territorial multiplier clamped [0.70, 1.43], min-8 of
last-10 validity rule, date-grouped predict-then-update).
FEED-FORCED DIVERGENCE (frozen here, before fitting): the territorial multiplier
uses the possession covariate ONLY (beta grid poss ∈ ±{0, .0025, .005, .0075, .010});
`big_chance` exists only in the 2025–2026 rich era, so its beta is absent, not
zero-fitted. NO X7 arm: `touches_opp_box` likewise exists only from 2025, so a
box-touch variant cannot be dev-evaluated over 2022–2025 (FEATURES.md).
Single-arm candidate.

- Target: total corners (stats feed). Primary line **9.5** (dev over-rate 0.547,
  closest to 0.5). Ladder 8.5 / 9.5 / 10.5, gate at 9.5.
- Arm: **Gate Zero** only.
- Warm-up 2021; dev scored 2022–2025 (n = 678 stats rows). Dev harness must not read 2026 rows.
- Baselines: league base rate (per-season NB from decay-weighted pre-season window, as PREREG_C_J1); naive trailing-10 through the same per-season NB size.
- Virgin: 2026 (n = 177), read ONCE, only if Gate Zero passes dev.
  Calibration = mean P(over 9.5) − actual, SE = sd(p_i − y_i)/√n.

## GATE LEGS (verbatim, frozen)
Dev gate — pooled dev LL at the primary line beats BOTH baselines (league base rate; naive trailing-10), else arm dead, no virgin read. Virgin legs — (i) LL ≤ Gate Zero's and ≤ best baseline's; (ii) calibration |mean P(over) − actual| ≤ 1.0pp clean PASS, breach within 1 SE = PROVISIONAL PASS, else FAIL; (iii) dev per-season sign check for both-pass (variant dev LL ≤ Gate Zero's in at least half the dev seasons). Both-pass: lower pooled virgin LL ships; one → ships; none → FAIL. Ties → simpler arm. If Gate Zero fails its dev gate, variants are moot, verdict FAIL, virgin NOT read.
(Single arm: leg (iii) and the both-pass rule are vacuous; Gate Zero passes iff it survives dev and virgin legs (i)–(ii).)

## Outputs
Engine `engine/corners/`; `results_dev.json` (+ CSV); `results_virgin.json`;
`fitted_params_virgin.json`; on PASS, `predictions/c_fi_virgin_predictions.csv`
(FT ladder + 1H/2H presentation via frozen corners constant 0.4631). Verdict `reports/C_FI_VERDICT.md`.
