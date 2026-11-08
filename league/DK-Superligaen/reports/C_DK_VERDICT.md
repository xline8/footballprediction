# C-DK verdict — PASS (calibration PROVISIONAL) — Gate Zero SHIPS

Prereg: `prereg/PREREG_C_DK.md` (frozen 6a0240b, before fitting).
Primary line 9.5. Dev pooled n = 579; virgin 2025/2026 n = 193,
read once, for both dev-passing arms.

## Dev results — pooled LL@9.5

| Arm / baseline | LL@9.5 |
|---|---|
| Gate Zero (X9) | 0.6861 |
| X7 (box touches) | 0.6854 |
| League base rate | 0.7473 |
| Naive trailing-10 | 0.7375 |

Both arms beat both baselines by wide margins → both pass the dev
gate. X7 per-season sign check vs Gate Zero: 0.6895 ≤ 0.6916,
0.6837 = 0.6837, 0.6830 = 0.6830 → 3/3.

## Virgin results (2025/2026, n = 193)

| Arm / baseline | LL@9.5 | Calibration (mean P − actual) |
|---|---|---|
| Gate Zero | 0.7038 | −1.19pp (SE 3.65pp) |
| X7 | 0.7038 | −1.19pp (SE 3.65pp) |
| League base rate | 0.7377 | — |
| Naive trailing-10 | 0.7465 | — |

## Gate arithmetic

- Leg (i): both arms' virgin LL 0.7038 ≤ Gate Zero's (equal) and
  ≤ best baseline 0.7377. PASS.
- Leg (ii): |−1.19pp| breaches the 1.0pp boundary by 0.19pp, which
  is within 1 SE (3.65pp) → **PROVISIONAL PASS**.
- Leg (iii): X7 sign check 3/3 (above).
- Both arms pass; their virgin predictions are **identical** — on
  the virgin fit both territorial betas fitted to exactly 0.0
  (Gate Zero β = [0, 0]; X7 β_bt = 0; γ = 0.3, r = 1.2096 for both),
  the same result C-J1 recorded: the box-touch trait is real in DK
  too (split-half r = 0.830/0.871, the strongest traits in the EDA)
  but earns exactly zero inside this multiplier structure. The
  frozen tie rule ships the simpler arm: **Gate Zero**.

**Ships:** Gate Zero (production corners pattern, X9 covariates),
fitted parameters in `engine/corners/fitted_params_virgin.json`,
virgin predictions in `predictions/c_dk_virgin_predictions.csv`
(193 rows; FT ladder + 1H/2H via the frozen corners constant
0.488). **DK joins the daily runner with corners.** Coordinator
verification: dev rerun reproduced pooled LLs exactly; virgin
LL@9.5 recomputed from the shipped predictions CSV = 0.703823,
matching the results JSON to 6dp.
