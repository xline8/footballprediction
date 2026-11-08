# Pre-registration — C-CL (Chile Liga de Primera corners model)

Frozen: 2026-11-10, before any fitting. Branch `build/cl-primera`.
Design authority: `analysis/MODEL_DESIGN.md` (C-CL); features X5,
X9-possession (Gate Zero internal) and X7 box touches (variant);
evidence EDA (corners for 0.333 / against 0.320; box touches
for 0.432). Reference: production
`model_corners_v3.py`; sibling analogue
`league/RU-PremierLeague/prereg/PREREG_C_RU.md` — its shared engine
is carried over verbatim in form (HL = 270 base rates, rolling-5
relative factors clamped [0.6, 1.7], core mean `mu_cs`, NB pmf grid
0..50, per-season gamma/beta/r fitting on prior-season walk-forward
rows only, gamma grid (0.0, 0.15, 0.3, 0.45, 0.6, 0.8), r clamped
[1.02, 5.0], territorial multiplier clamped [0.70, 1.43], min-8 of
last-10 validity rule, date-grouped predict-then-update state).
Phase rule (frozen, MODEL_DESIGN): all rows are phase `regular`;
no phase feature anywhere.
Calibration = **actual − predicted** everywhere in this build.

- Target: total corners (stats feed). Primary line **9.5**
  (dev-period over-rate 0.508, closest to 0.5; the 8.5 over-rate
  is 0.613). Ladder 8.5 / 9.5 / 10.5 reported, gate at 9.5.
- Arms: **Gate Zero** — the production pattern with the
  possession-only territorial covariate: beta grid exactly as the
  possession part of PREREG_C_RU (poss ∈ ±{0, .0025, .005, .0075,
  .010}); and **BOXT** — the same pattern with the box-touch
  territorial covariate (X7, ADOPTED in FEATURES: touches_opp_box
  present across the era, split-half r = 0.432) on the engine's
  box-touch beta grid. Both-pass rule as in the other CL preregs:
  if both pass all virgin legs, the lower pooled virgin LL@9.5
  ships; ties go to Gate Zero.
- Training seed 2021; dev evaluation 2022–2024
  (stats rows n = 719). Dev harness must not read 2025 /
  2026 rows.
- Baselines: league base rate (per-season NB from decay-weighted
  pre-season window, as PREREG_C_J1) and naive trailing-10 (X5)
  through the same per-season NB size.
- Virgin: 2025 (stats rows n = 240), read ONCE, only for
  dev-passing arms. Calibration at 9.5 = actual − mean
  predicted, SE = sd(y_i − p_i)/√n.
- Halves: period splits exist from 2023; the frozen corners
  constant 0.4644 (EDA) is used for 1H/2H presentation only.

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev LL@9.5 beats BOTH baselines (league base rate; naive trailing-10), else the arm is dead, no virgin read. Virgin legs — (i) LL@9.5 ≤ Gate Zero's and ≤ best baseline's; (ii) calibration |actual − mean P(over 9.5)| ≤ 1.0pp, SE reported, breach within 1 SE = PROVISIONAL PASS; (iii) dev per-season sign check for the variant (≥2 of 3 dev seasons with LL ≤ Gate Zero's). Both-pass: lower pooled virgin LL@9.5 ships; one passes → it ships; none → FAIL. If Gate Zero fails its dev gate, the variant is moot, verdict FAIL, virgin NOT read.

Mechanical reading: an arm passes iff it survives the dev gate
AND passes virgin legs (i)–(ii) (PROVISIONAL counts, recorded as
such) AND, for BOXT, leg (iii). Gate Zero dev failure ⇒ FAIL,
virgin NOT read.

## Outputs

Engine `engine/corners/`; `results_dev.json` (+ CSV);
`results_virgin.json`; `fitted_params_virgin.json`; on PASS,
`predictions/c_cl_virgin_predictions.csv` (FT ladder 8.5/9.5/10.5;
1H/2H presentation via frozen corners constant 0.4644). Verdict `reports/C_CL_VERDICT.md`.
