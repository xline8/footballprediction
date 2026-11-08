# K-DE2 verdict — PASS (calibration PROVISIONAL for the shipped arm) — X8 SHIPS

Prereg: `prereg/PREREG_K_DE2.md` (frozen 4261ad8, before fitting).
Primary line **4.5** (dev over-rate 0.434). Dev pooled n = 918;
virgin 2025/2026 n = 306, read once, for both dev-passing arms.
Target: stats-feed yellows (the feed check is in
DATA_UNDERSTANDING §4 — BE/DK shape, no event-unified amendment).

## Dev results — pooled LL@4.5

| Arm / baseline | LL@4.5 |
|---|---|
| Gate Zero | 0.6849 |
| X8 (referee) | 0.6779 |
| League base rate | 0.6901 |
| Naive trailing-10 | 0.6952 |

Both arms beat both baselines → both pass the dev gate. X8's
per-season sign check vs Gate Zero: **3/3** (better in every dev
season: 0.6931/0.6379/0.7026 vs 0.6967/0.6475/0.7104) — the
referee arm's dev gain (−0.0070 LL) is the largest X8 dev gain in
the program, on a moderate trait (EDA F9, r = 0.470) paired with
the program's second-strongest team yellows trait (F2, 0.558).

## Virgin results (2025/2026, n = 306)

| Arm / baseline | LL@4.5 | Calibration (mean P − actual) |
|---|---|---|
| Gate Zero | 0.6807 | −0.14pp (SE 2.83pp) |
| X8 | 0.6734 | +1.08pp (SE 2.81pp) |
| League base rate | 0.6902 | — |
| Naive trailing-10 | 0.6823 | — |

## Gate arithmetic

- Leg (i): both pass. Gate Zero 0.6807 ≤ best baseline 0.6823
  (by 0.0016); X8 0.6734 ≤ Gate Zero and ≤ both baselines.
- Leg (ii): Gate Zero's calibration is **−0.14pp — inside the
  1.0pp boundary: CLEAN**. X8 breaches the boundary by 0.08pp,
  within 1 SE (2.81pp) → **PROVISIONAL PASS**.
- Leg (iii): X8 sign check 3/3 (above).
- Both arms pass; the both-pass rule ships the lower pooled
  virgin LL: **X8** (0.6734 < 0.6807). Unlike BE — where the
  referee arm won dev and gave it all back in the virgin — DE-2's
  X8 holds its dev advantage in the virgin window and wins the
  both-pass rule honestly. The shipped arm's verdict is
  PROVISIONAL because its calibration, not Gate Zero's, is the
  one that ships.

**Ships:** X8 (production cards pattern + referee covariate,
shrunk toward the league mean with prior weight 8; fixtures
without a published appointment fall back to Gate Zero — no
imputation), fitted parameters in
`engine/cards/fitted_params_virgin.json`, virgin predictions in
`predictions/k_de2_virgin_predictions.csv` (306 rows; FT ladder
3.5/4.5/5.5 + 1H/2H via the frozen yellows constant 0.346).
**DE-2 joins the daily runner with cards.**
Builder verification: virgin LL@4.5 recomputed from the shipped
predictions CSV (actuals joined from the matches CSV) = 0.6734,
matching the results JSON; calibration recomputed +1.08pp.
