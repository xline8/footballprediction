# Pre-registration — C-CZ (CZ-Liga corners model)

Frozen: 2026-11-10, before any fitting. Branch `build/cz-liga`.
Design authority: `analysis/MODEL_DESIGN.md` (C-CZ); features X5,
X9 (reduced form); evidence F1/F2. Reference: production
`model_corners_v3.py`; RO analogue `PREREG_C_RO.md` — its shared
engine is carried over in form (HL = 270 base rates, rolling-5
relative factors clamped [0.6, 1.7], core mean `mu_cs`, NB pmf grid
0..50, per-season gamma/beta/r fitting on prior-season walk-forward
rows only, gamma grid (0.0, 0.15, 0.3, 0.45, 0.6, 0.8), r clamped
[1.02, 5.0], territorial multiplier clamped [0.70, 1.43], min-8 of
last-10 validity rule, date-grouped predict-then-update state).

- Target: total corners (stats feed). Primary line **10.5** (dev
  over-rate 0.4565 vs 9.5 → 0.5753; 10.5 is closest to 0.5).
  Ladder 9.5 / 10.5 / 11.5 reported, gate at 10.5.
- Arms: **Gate Zero only** — production pattern with the CZ
  covariate set: `BallPossesion` alone (beta grid exactly as
  PREREG_C_J1: poss ∈ ±{0, .0025, .005, .0075, .010}). The
  reference's `big_chance` covariate and the X7 box-touches variant
  are NOT registered: both keys exist only from 2025/2026, so no
  dev-era fit or test is possible (FEATURES X7/X9). No replacement
  variant is invented.
- Training seed 2021/2022; dev evaluation 2022/2023–2024/2025
  (stats-target n = 802). Dev harness must not read 2025/2026 /
  2026/2027 rows.
- Baselines: league base rate (per-season NB from decay-weighted
  pre-season window, as PREREG_C_J1) and naive trailing-10 (X5)
  through the same per-season NB size.
- Virgin: 2025/2026 (stats n = 270), read ONCE, only if Gate Zero
  passes the dev gate. Calibration at 10.5 with
  SE = sd(p_i − y_i)/√n.

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev LL@10.5 beats BOTH baselines (league base rate; naive trailing-10), else the candidate is dead, no virgin read. Virgin legs — (i) LL@10.5 ≤ best baseline's; (ii) calibration |mean P(over 10.5) − actual| ≤ 1.0pp, SE reported, breach within 1 SE = PROVISIONAL PASS. If Gate Zero passes all legs it ships; if none passes, C-CZ verdict is FAIL and nothing ships.

(Single-arm candidate: the both-pass rule and leg (iii) of the
multi-arm preregs do not apply. Gate Zero dev failure ⇒ FAIL,
virgin NOT read.)

## Outputs

Engine `engine/corners/`; `results_dev.json` (+ CSV);
`results_virgin.json`; `fitted_params_virgin.json`; on PASS,
`predictions/c_cz_virgin_predictions.csv` (FT ladder 9.5/10.5/11.5
only — FT-only market: halves_share_1h = null, no dev-era period
splits, MODEL_DESIGN). Verdict `reports/C_CZ_VERDICT.md`.
