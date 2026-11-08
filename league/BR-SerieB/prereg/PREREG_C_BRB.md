# Pre-registration — C-BRB (BR-SerieB corners model)

Frozen: 2026-11-09, before any fitting. Branch `build/br-serieb`.
Design authority: `analysis/MODEL_DESIGN.md` (C-BRB); features X5,
X7, X9. Reference: production `model_corners_v3.py`; BR analogue
`PREREG_C_BR.md` — its shared engine is carried over verbatim in
form (HL = 270 base rates, rolling-5 relative factors clamped
[0.6, 1.7], core mean `mu_cs`, NB pmf grid 0..50, per-season
gamma/beta/r fitting on prior-season walk-forward rows only,
gamma grid (0.0, 0.15, 0.3, 0.45, 0.6, 0.8), r clamped [1.02, 5.0],
territorial multiplier clamped [0.70, 1.43], min-8 of last-10
validity rule, date-grouped predict-then-update state).

- Target: total corners (stats feed). Primary line **10.5** (dev
  over-rate 0.454, closest to 0.5). Ladder 9.5/10.5/11.5 reported.
- Arms: **Gate Zero (X9)** — production covariates `BallPossesion`
  + `big_chance`, beta grids exactly as PREREG_C_BR (poss ∈
  ±{0, .0025, .005, .0075, .010}, bc ∈ ±{0, .025, .05, .075, .10});
  **X7** — covariates replaced by `touches_opp_box` for/against,
  beta_bt ∈ ±{0, .01, .02, .03, .04}. X7 coverage in Série B is
  partial before 2024 (~27% 2021, ~28% 2022, ~64% 2023, 100% from
  2024); the min-8 rule makes the multiplier inactive where the
  window cannot fill — reported per season, not a defect.
- Training seed 2021; dev evaluation 2022–2024 (n = 1,140). Dev
  harness must not read 2025 / 2026 rows.
- Baselines: league base rate (per-season NB from decay-weighted
  pre-season window, as PREREG_C_BR) and naive trailing-10 (X5)
  through the same per-season NB size.
- Virgin: 2025 (n = 380), read ONCE, only for dev-passing arms.
  Calibration at 10.5 = ACTUAL − PREDICTED (this build's stated
  convention), SE = sd(y_i − p_i)/√n. 2026 NOT read.

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev LL@10.5 beats BOTH baselines (league base rate; naive trailing-10), else arm dead, no virgin read. Virgin legs — (i) LL@10.5 ≤ Gate Zero's and ≤ best baseline's; (ii) calibration |actual − predicted| ≤ 1.0pp, SE reported, breach within 1 SE = PROVISIONAL PASS; (iii) dev per-season sign check for both-pass. Both-pass: both → lower pooled virgin LL ships; one → ships; none → FAIL.

Mechanical reading as in PREREG_S_BRB (variant sign check ≥2 of 3
dev seasons; ties → Gate Zero; Gate Zero dev failure ⇒ FAIL,
virgin NOT read).

## Outputs

Engine `engine/corners/`; `results_dev.json` (+ CSV);
`results_virgin.json`; `fitted_params_virgin.json`; on PASS,
`predictions/c_brb_virgin_predictions.csv` (FT ladder 9.5/10.5/11.5;
1H/2H presentation-only via frozen corners constant 0.472 with the
fitted NB r, lines 1H 3.5/4.5/5.5, 2H 4.5/5.5/6.5). Verdict
`reports/C_BRB_VERDICT.md`.
