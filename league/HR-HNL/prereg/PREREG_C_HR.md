# Pre-registration — C-HR (HR-HNL corners model)

Frozen: 2026-11-10, before any fitting. Branch `build/hr-hnl`.
Design authority: `analysis/MODEL_DESIGN.md` (C-HR); features X5, X9 (full), X7;
evidence F2/F5. Reference: production `model_corners_v3.py` as frozen in
`PREREG_C_J1.md` (HL = 270 base rates, rolling-5 relative factors clamped [0.6, 1.7], NB pmf grid 0..50, per-season gamma/beta/r fitting
on prior-season walk-forward rows only, gamma grid (0.0, 0.15, 0.3, 0.45, 0.6, 0.8),
r clamped [1.02, 5.0], territorial multiplier clamped [0.70, 1.43], min-8 of
last-10 validity rule, date-grouped predict-then-update).
Gate Zero carries the FULL X9 multiplier (possession + big_chance trailing
differentials): both keys exist in every HNL season, so no feed-forced
divergence of the FI kind applies. The X7 arm replaces the territorial
multiplier with the opp-box-touches multiplier (J1 pattern, beta grid
±{0, .01, .02, .03, .04}); where a team's touches window fails the
min-8 rule the X7 multiplier is 1.0 for that match and the match is
counted in the arm's reported active share.

- Target: total corners (stats feed). Primary line **8.5** (dev over-rate 0.509).
  Ladder 7.5 / 8.5 / 9.5, gate at 8.5.
- Arms: **Gate Zero** (X9); **X7** (box touches).
- Warm-up 2021/2022; dev scored 2022/2023–2024/2025 (n = 540 stats rows). Dev harness must not read 2025/2026 rows.
- Baselines: league base rate (per-season NB from decay-weighted pre-season window, as PREREG_C_J1); naive trailing-10 through the same per-season NB size.
- Virgin: 2025/2026 (n = 180), read ONCE, only for dev-passing arms.
  Calibration = mean P(over 8.5) − actual, SE = sd(p_i − y_i)/√n.

## GATE LEGS (verbatim, frozen)
Dev gate — pooled dev LL at the primary line beats BOTH baselines (league base rate; naive trailing-10), else arm dead, no virgin read. Virgin legs — (i) LL ≤ Gate Zero's and ≤ best baseline's; (ii) calibration |mean P(over) − actual| ≤ 1.0pp clean PASS, breach within 1 SE = PROVISIONAL PASS, else FAIL; (iii) dev per-season sign check for both-pass (variant dev LL ≤ Gate Zero's in at least half the dev seasons — ≥2 of 3). Both-pass: lower pooled virgin LL ships; one → ships; none → FAIL. Ties → simpler arm. If Gate Zero fails its dev gate, variants are moot, verdict FAIL, virgin NOT read.

## Outputs
Engine `engine/corners/`; `results_dev.json` (+ CSV); `results_virgin.json`;
`fitted_params_virgin.json`; on PASS, `predictions/c_hr_virgin_predictions.csv`
(FT ladder + 1H/2H presentation via frozen corners constant 0.4793). Verdict `reports/C_HR_VERDICT.md`.
