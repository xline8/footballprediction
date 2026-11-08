# T-SE verdict — PASS (arm A ships)

Prereg: `league/SE-Allsvenskan/prereg/PREREG_T_SE.md` (frozen in
commit 62320f5, before any fitting). Primary line 26.5. Dev =
walk-forward evaluation seasons 2022–2024 (pooled n = 720);
virgin = 2025 (n = 240), read once.

## Dev results (pooled LL@26.5)

| Arm / baseline | LL@26.5 | Sign vs A |
|---|---|---|
| A (v1 pattern) | 0.6658 | — |
| B (v2 level layer) | 0.6656 | 1/3 |
| C (E9 trailing-r) | 0.6660 | 1/3 |
| League base rate | 0.6945 | |
| Naive trailing-10 | 0.6803 | |

All three arms beat both baselines on dev.

## Virgin results (2025, n = 240; actual over-26.5 rate 0.4958)

| Arm | LL@26.5 | Calibration | SE |
|---|---|---|---|
| A | 0.6660 | +0.31pp | 3.14pp |
| B | 0.6670 | +0.85pp | 3.14pp |
| C | 0.6660 | +0.42pp | 3.14pp |
| League base rate | 0.6937 | +1.82pp | |
| Naive trailing-10 | 0.6687 | +1.21pp | |

## Gate arithmetic

- Dev gate: A, B, C all pass (above).
- Virgin leg (i) vs the reference arm (A): B 0.6670 > A 0.6660
  **fails**; C 0.666013 ≤ A 0.666030 ✓ (by 0.000017) and ≤ best
  baseline 0.6687 ✓; A ≤ best baseline ✓.
- Virgin leg (ii): all three arms are inside the 1.0pp boundary
  outright (A +0.31, B +0.85, C +0.42pp) — clean, no provisional
  reading needed.
- Leg (iii): B and C each beat A in only 1 of 3 dev seasons → both
  **fail** the sign check. Only A passes every leg.

**Verdict: PASS (clean). Arm A ships** — the v1 pattern (ratings +
NB + naive ensemble), NB r_A = 55.05 fitted on dev. Predictions:
`predictions/t_se_virgin_predictions.csv` (240 rows; FT ladder
25.5/26.5/27.5; 1H/2H presentation-only via the frozen shots
constant 0.457). Fitted params:
`engine/total_shots/fitted_params_virgin.json`. Independent
recomputation of the virgin LL@26.5 from the predictions CSV
reproduces 0.666030 exactly. Predictions-only product. (T-SE is a
separate corpus from the top-5 total-shots prospective trial;
neither contaminates the other.)
