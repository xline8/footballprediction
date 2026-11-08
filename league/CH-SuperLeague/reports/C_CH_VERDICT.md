# C-CH verdict — PASS (calibration PROVISIONAL) — Gate Zero SHIPS

Prereg: `prereg/PREREG_C_CH.md` (frozen ccf74a9, before fitting).
Primary line **10.5** (dev over-rate 0.447). Dev pooled n = 636;
virgin 2025/2026 n = 228, read once, for both dev-passing arms.

## Dev results — pooled LL@10.5

| Arm / baseline | LL@10.5 |
|---|---|
| Gate Zero (X9) | 0.6978 |
| X7 (box touches) | 0.6978 |
| League base rate | 0.7167 |
| Naive trailing-10 | 0.7135 |

Both arms beat both baselines → both pass the dev gate.

## Virgin results (2025/2026, n = 228)

| Arm / baseline | LL@10.5 | Calibration (mean P − actual) |
|---|---|---|
| Gate Zero | 0.6906 | +1.06pp (SE 3.31pp) |
| X7 | 0.6906 | +1.06pp (SE 3.31pp) |
| League base rate | 0.6961 | — |
| Naive trailing-10 | 0.7000 | — |

## Gate arithmetic

- Leg (i): both arms' virgin LL 0.6906 ≤ Gate Zero's (equal) and
  ≤ best baseline 0.6961. PASS.
- Leg (ii): |+1.06pp| breaches the 1.0pp boundary by 0.06pp, within
  1 SE (3.31pp) → **PROVISIONAL PASS**.
- Leg (iii): X7's dev predictions are identical to Gate Zero's, so
  the sign check is 3/3 by equality.
- Both arms pass; their virgin predictions are **identical** — on
  the virgin fit both territorial betas fitted to exactly 0.0
  (Gate Zero β = [0, 0]; X7 β_bt = 0; γ = 0.15, r = 1.1261 for both),
  the same result C-J1 and C-DK recorded: the box-touch trait is
  real in CH too (split-half r = 0.933/0.835, the strongest traits
  in the EDA) but earns exactly zero inside this multiplier
  structure. The frozen tie rule ships the simpler arm:
  **Gate Zero**.

**Ships:** Gate Zero (production corners pattern, X9 covariates),
fitted parameters in `engine/corners/fitted_params_virgin.json`,
virgin predictions in `predictions/c_ch_virgin_predictions.csv`
(228 rows; FT ladder + 1H/2H via the frozen corners constant
0.471). **CH joins the daily runner with corners.** Coordinator
verification: virgin LL@10.5 recomputed from the shipped
predictions CSV = 0.6906, matching the results JSON.
