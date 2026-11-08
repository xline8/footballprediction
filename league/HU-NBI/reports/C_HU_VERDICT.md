# C-HU-NBI (corners) — VERDICT: PASS (PROVISIONAL) — Gate Zero ships

Pattern: model_corners_v3 port, possession-only territorial covariate
(the feed has no big chances / box touches). Primary line 9.5.
Halves: FT-only (no period splits; corners_1h_share null).

Dev (n=588, expanding walk-forward):
| arm | dev LL@9.5 | base LL | naive LL | per-season sign |
|---|---|---|---|---|
| gate_zero | 0.6931 | 0.7417 | 0.7384 | beats both baselines in all 3 seasons |
| plain | 0.6969 | 0.7417 | 0.7384 | beats both baselines in all 3 seasons |

Both arms pass the dev gate → virgin read ONCE (2025/2026, n=198),
fit on 2021/22–2024/25:
| arm | virgin LL@9.5 | best baseline LL | calibration (actual − predicted) |
|---|---|---|---|
| gate_zero | 0.6755 | 0.7121 (base) / 0.7267 (naive) | −1.56 pp, 1 SE = 3.55 pp |
| plain | 0.6946 | 0.7121 / 0.7267 | −1.49 pp, 1 SE = 3.55 pp |

Gate legs: (i) LL beats best baseline ✓ both arms; (ii) calibration
|−1.56| > 1 pp but ≤ 1 SE → PROVISIONAL PASS. Gate Zero has the lower
virgin LL and ships per the tie rule. Unlike most leagues in this
program, the territorial multiplier is genuinely active here:
β_poss = 0.005 fitted on the virgin fit window, active on 190/198
virgin rows (γ = 0.0, NB r = 1.086, fit_n = 775).

Ships: gate_zero, params in engine/corners/fitted_params_virgin.json,
predictions in predictions/c_hu_virgin_predictions.csv (force-added).
Coordinator recomputed the virgin LL from that CSV: 0.6755, exact.
