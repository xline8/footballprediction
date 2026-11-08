# Pre-registration — C-CA (CA-PremierLeague corners model)

Frozen: 2026-11-10, before any fitting. Branch `build/ca-premier`.
Design authority: `analysis/MODEL_DESIGN.md` (C-CA); features X5,
X9 (full form); evidence per `analysis/EDA.md`. Reference:
production `model_corners_v3.py`; J1 analogue `PREREG_C_J1.md` —
its shared engine is carried over in form (HL = 270 base rates,
rolling-5 relative factors clamped [0.6, 1.7], core mean `mu_cs`,
NB pmf grid 0..50, per-season gamma/beta/r fitting on prior-season
walk-forward rows only, gamma grid (0.0, 0.15, 0.3, 0.45, 0.6, 0.8),
r clamped [1.02, 5.0], territorial multiplier clamped [0.70, 1.43],
min-8 of last-10 validity rule, date-grouped predict-then-update
state).

- Target: total corners (stats feed, present 699/699). Primary
  line **9.5** (dev over-rate 0.486607 vs 8.5 → 0.616071; 9.5 is
  closest to 0.5). Ladder 8.5 / 9.5 / 10.5 reported, gate at 9.5.
- Arms: **Gate Zero only** — production pattern with the full CA
  covariate set (FEATURES X9 adopted in full form: BOTH
  `BallPossesion` and `big_chance` exist in all 699 payloads):
  betas fitted by the J1 grid procedure (beta_poss ∈ ±{0, .0025,
  .005, .0075, .010}; beta_bc ∈ ±{0, .025, .05, .075, .10}). The
  X7 box-touches variant is NOT registered: `touches_opp_box`
  exists in only 34/28/22 dev-era matches of 2021/22/23, so the
  min-8 trailing rule cannot be filled for most of the dev window
  (FEATURES X7). No replacement variant is invented.
- Training seed 2021; dev evaluation 2022–2024 (stats-target
  n = 336). Dev harness must not read 2025 / 2026 rows.
- Baselines: league base rate (per-season NB from decay-weighted
  pre-season window, as PREREG_C_J1) and naive trailing-10 (X5)
  through the same per-season NB size.
- Virgin: 2025 (stats n = 112), read ONCE, only if Gate Zero
  passes the dev gate. Calibration at 9.5 with
  SE = sd(p_i − y_i)/√n.

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev LL@9.5 beats BOTH baselines (league base rate; naive trailing-10), else the candidate is dead, no virgin read. Virgin legs — (i) LL@9.5 ≤ best baseline's; (ii) calibration |mean P(over 9.5) − actual| ≤ 1.0pp, SE reported, breach within 1 SE = PROVISIONAL PASS. If Gate Zero passes all legs it ships; if none passes, C-CA verdict is FAIL and nothing ships.

(Single-arm candidate: the both-pass rule and leg (iii) of the
multi-arm preregs do not apply. Gate Zero dev failure ⇒ FAIL,
virgin NOT read.)

## Outputs

Engine `engine/corners/`; `results_dev.json` (+ CSV);
`results_virgin.json`; `fitted_params_virgin.json`; on PASS,
`predictions/c_ca_virgin_predictions.csv` (FT ladder 8.5/9.5/10.5
plus 1H/2H presentation-only via frozen corners constant
0.466319). Verdict `reports/C_CA_VERDICT.md`.
