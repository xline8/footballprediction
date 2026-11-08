# Pre-registration — C-GR (GR-SuperLeague corners model)

Frozen: 2026-11-09, before any fitting. Branch `build/gr-super`.
Design authority: `analysis/MODEL_DESIGN.md` (C-GR); features X5,
X7, X9; evidence EDA (corners for 0.833 / against 0.714; box touches
0.953 / 0.855; possession 0.931; big chances 0.860). Reference:
production `model_corners_v3.py`; PL analogue `PREREG_C_PL.md` —
its shared engine is carried over verbatim in form (HL = 270 base
rates, rolling-5 relative factors clamped [0.6, 1.7], core mean
`mu_cs`, NB pmf grid 0..50, per-season gamma/beta/r fitting on
prior-season walk-forward rows only, gamma grid (0.0, 0.15, 0.3,
0.45, 0.6, 0.8), r clamped [1.02, 5.0], territorial multiplier
clamped [0.70, 1.43], min-8 of last-10 validity rule, date-grouped
predict-then-update state).
Phase rule (frozen, MODEL_DESIGN): all phases are ordinary rows;
no phase feature anywhere.
Calibration = **actual − predicted** everywhere in this build.

- Target: total corners (stats feed). Primary line **8.5**
  (dev-period over-rate 0.517, closest to 0.5; the 9.5 over-rate
  is 0.386). Ladder 7.5 / 8.5 / 9.5 reported, gate at 8.5.
- Arms: **Gate Zero (X9)** — production covariates `BallPossesion`
  + `big_chance`, beta grids exactly as PREREG_C_J1 (poss ∈
  ±{0, .0025, .005, .0075, .010}, bc ∈ ±{0, .025, .05, .075, .10});
  **X7** — covariates replaced by `touches_opp_box` for/against,
  beta_bt ∈ ±{0, .01, .02, .03, .04}. X7 coverage in GR: 0.0% in
  2021/2022, 82.5% in 2022/2023, 89.6% in 2023/2024, 97.9% in
  2024/2025, 100% in the virgin 2025/2026; the min-8 rule makes the
  multiplier inactive where the window cannot fill — reported per
  season, not a defect.
- Training seed 2021/2022; dev evaluation 2022/2023–2024/2025
  (n = 716). Dev harness must not read 2025/2026 / 2026/2027 rows.
- Baselines: league base rate (per-season NB from decay-weighted
  pre-season window, as PREREG_C_J1) and naive trailing-10 (X5)
  through the same per-season NB size.
- Virgin: 2025/2026 (n = 236), read ONCE, only for dev-passing arms.
  Calibration at 8.5 = actual − mean predicted, SE = sd(y_i − p_i)/√n.

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev LL@8.5 beats BOTH baselines (league base rate; naive trailing-10), else arm dead, no virgin read. Virgin legs — (i) LL@8.5 ≤ Gate Zero's and ≤ best baseline's; (ii) calibration |actual − mean P(over 8.5)| ≤ 1.0pp, SE reported, breach within 1 SE = PROVISIONAL PASS; (iii) dev per-season sign check for both-pass. Both-pass: both → lower pooled virgin LL ships; one → ships; none → FAIL.

Mechanical reading as in PREREG_S_GR (variant sign check ≥2 of 3 dev
seasons; ties → Gate Zero; Gate Zero dev failure ⇒ FAIL, virgin
NOT read).

## Outputs

Engine `engine/corners/`; `results_dev.json` (+ CSV);
`results_virgin.json`; `fitted_params_virgin.json`; on PASS,
`predictions/c_gr_virgin_predictions.csv` (FT ladder 7.5/8.5/9.5;
1H/2H presentation-only via frozen corners constant 0.4862 with the
fitted NB r, lines 1H 3.5/4.5/5.5, 2H 4.5/5.5/6.5). Verdict
`reports/C_GR_VERDICT.md`.
