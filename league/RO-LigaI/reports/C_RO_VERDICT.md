# Verdict — C-RO (RO-LigaI corners)

**PASS (PROVISIONAL) — Gate Zero ships.**

Dev (pooled, stats-target n = 924, LL@8.5): Gate Zero 0.6842 vs
league base rate 0.7602 and naive trailing-10 0.7501 → dev gate
PASS (single-arm candidate; X7/big-chance variants not registered
— the keys exist only from 2025/2026).

Virgin (2025/2026, n = 315):

| | LL@8.5 | Mean P(over) | Actual |
|---|---|---|---|
| Gate Zero | 0.6646 | 0.5986 | 0.6286 |
| League base rate | 0.7673 | — | — |
| Naive trailing-10 | 0.7625 | — | — |

Gate arithmetic (PREREG_C_RO): leg (i) LL 0.6646 ≤ best baseline
0.7625 ✓. Leg (ii) calibration: diff = −3.00pp, SE = 2.74pp.
|−3.00pp| > 1.0pp, but the breach beyond the boundary (2.00pp) is
within 1 SE (2.74pp) → **PROVISIONAL PASS**. The model
under-predicts corner overs in the virgin season (mean P 0.599 vs
actual 0.629); the provisional label records exactly that.

Ships: Gate Zero (possession-only covariate; fitted gamma/r/beta
in `engine/corners/fitted_params_virgin.json`). Predictions:
`predictions/c_ro_virgin_predictions.csv` (n = 315; headline LL
and calibration recomputed from this file independently — exact
match). 1H/2H presentation via frozen corners constant 0.477.
