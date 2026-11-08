# Verdict — C-RU1 (Russia 1. Division corners)

**PASS (PROVISIONAL — calibration leg). Gate Zero ships.**

## Dev (stats n = 855, LL @ 8.5)

| arm | LL @ 8.5 | calibration |
|---|---|---|
| Gate Zero (possession-only covariate) | 0.695540 | +2.66 pp |
| league base | 0.728439 | |
| naive trailing-10 | 0.729279 | |

Per-season LL: 0.694090 / 0.691829 / 0.701333. Dev gate: 0.695540
beats BOTH baselines — PASS.

## Virgin (2025/2026, stats n = 287, LL @ 8.5)

| arm | LL @ 8.5 | calibration | SE |
|---|---|---|---|
| Gate Zero | 0.698888 | +3.28 pp | 2.97 |
| league base | 0.746916 | | |
| naive trailing-10 | 0.744605 | | |

Leg (i): 0.698888 ≤ best baseline 0.744605 PASS. Leg (ii):
|calibration| = 3.28 pp > 1.0 pp, but the excess over the
boundary (2.28 pp) is within 1 SE (2.97) → **PROVISIONAL PASS**.
Gate Zero is the only registered arm (X7 data absent; the
big-chance half of the RU-Premier X9 pair is absent — possession
only, per the prereg), so it ships.

Ships: Gate Zero with its fitted virgin params
(`engine/corners/fitted_params_virgin.json`); virgin predictions
in `predictions/c_ru1_virgin_predictions.csv` (FT ladder
7.5/8.5/9.5 only — this league has no period splits, so no halves
presentation exists).

Coordinator notes: (1) all numbers recomputed from
`engine/corners/predictions_dev.csv` and
`predictions_virgin_all.csv`; (2) the inherited engine's virgin
path never called its own predictions exporter (latent defect
from the RU-Premier build, where corners failed and the exporter
never fired) — fixed in `engine/corners/harness.py`, and the
shipped CSV was produced by that exporter with the fitted params.
