# Pre-registration — C-TH (Thailand Thai League 1 corners model)

Frozen: 2026-11-10, before any fitting. Branch `build/th-thaileague`.
Design authority: `analysis/MODEL_DESIGN.md` (C-TH); features X5, X7,
X9 (FEATURES.md); evidence EDA (corners for 0.690 / against 0.506;
touches_opp_box 0.819 / 0.751; possession 0.849 / 0.849; big chance
0.564 / 0.493). Reference: production `model_corners_v3.py`; sibling
analogue `league/J1/prereg/PREREG_C_J1.md` — the shared engine is
carried over verbatim in form (HL = 270 base rates, rolling-5
relative factors clamped [0.6, 1.7], core mean `mu_cs`, NB pmf grid
0..50, per-season gamma/beta/r fitting on prior-season walk-forward
rows only, gamma grid (0.0, 0.15, 0.3, 0.45, 0.6, 0.8), r clamped
[1.02, 5.0], territorial multiplier clamped [0.70, 1.43], min-8 of
last-10 validity rule, date-grouped predict-then-update state).
Phase rule (frozen): all rows are phase `regular`; no phase feature.
Calibration = **actual − predicted** everywhere in this build.

- Target: total corners (stats feed). Primary line **9.5**
  (scored-dev over-rate 0.498, closest to 0.5). Ladder 8.5 / 9.5 /
  10.5 reported, gate at 9.5.
- Arms: **Gate Zero (X9)** — production covariates `BallPossesion` +
  `big_chance`, beta grids exactly as PREREG_C_J1 (poss ∈ ±{0, .01,
  .02, .03, .04}; bc ∈ ±{0, .025, .05, .075, .10}; joint 9×9 grid,
  multiplier `exp(beta·z)` clamped [0.70, 1.43]);
  **Arm X7** — identical engine; territorial covariate =
  `touches_opp_box` for/against, beta_bt ∈ ±{0, .01, .02, .03, .04},
  multiplier clamped [0.70, 1.43], inactive where a team's trailing
  touches are missing (coverage 174/240 in the seed season is the
  documented cause of early inactivity).
- Training seed 2022/2023; dev evaluation 2023/2024–2024/2025
  (stats rows n = 480). Dev harness must not read 2025/2026 /
  2026/2027 rows.
- Baselines: league base rate (per-season NB from decay-weighted
  pre-season window, as PREREG_C_J1) and naive trailing-10 (X5)
  through the same per-season NB size.
- Virgin: 2025/2026 (stats rows n = 240), read ONCE, only for arms
  passing the dev gate. Calibration at 9.5 = actual − mean
  predicted, SE = sd(y_i − p_i)/√n.
- Halves: 1H/2H presentation via the frozen corners constant 0.4622.

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev LL@9.5 beats BOTH baselines (league base rate; naive trailing-10), else the arm is dead, no virgin read. Virgin legs — (i) LL@9.5 ≤ Gate Zero's AND ≤ best baseline's (Gate Zero: ≤ best baseline's); (ii) calibration |actual − mean P(over 9.5)| ≤ 1.0pp, SE reported, breach within 1 SE = PROVISIONAL PASS; (iii) dev per-season sign check for both-pass (variant dev LL@9.5 ≤ Gate Zero's in ≥1 of 2 dev seasons). Both-pass: both → lower pooled virgin LL ships; one → ships; none → FAIL.

Mechanical reading: an arm passes iff it survives the dev gate AND
passes virgin legs (i)–(ii) (PROVISIONAL counts, recorded as such)
AND, for the variant, leg (iii). Ties → simpler arm (Gate Zero
before X7). Gate Zero dev failure ⇒ variants moot, FAIL, virgin
NOT read.

## Outputs

Engine `engine/corners/`; `results_dev.json` (+ CSV);
`results_virgin.json`; `fitted_params_virgin.json`; on PASS,
`predictions/c_th_virgin_predictions.csv` (FT ladder 8.5/9.5/10.5
+ 1H/2H presentation via frozen constant 0.4622). Verdict
`reports/C_TH_VERDICT.md`.
