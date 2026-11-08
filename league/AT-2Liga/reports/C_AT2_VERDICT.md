# Verdict — C-AT2 (Austria 2. Liga corners)

**FAIL — at the virgin gate (legs i and ii). Gate Zero passed dev
and dies on the virgin read. Nothing ships.**

## Dev (walk-forward; scored 2022/2023–2024/2025, stats n = 708, LL @ 9.5)

| arm | LL @ 9.5 |
|---|---|
| Gate Zero (possession-only covariate) | 0.703837 |
| league base rate | 0.731171 |
| naive trailing-10 | 0.733235 |

Per-season LL: 0.681643 / 0.701040 / 0.728689. Dev gate: 0.703837
beats BOTH baselines — PASS.

## Virgin (2025/2026, stats n = 210, LL @ 9.5)

| arm | LL @ 9.5 | calibration (actual − pred) | SE |
|---|---|---|---|
| Gate Zero | 0.680691 | −7.88 pp | 3.37 pp |
| league base rate | 0.670109 | | |
| naive trailing-10 | 0.673478 | | |

Leg (i): 0.680691 ≤ best baseline 0.670109 — **FAIL** (Gate Zero
loses to *both* baselines on the virgin window). Leg (ii):
|calibration| = 7.88 pp > 1.0 pp, and the excess over the boundary
(6.88 pp) is beyond 1 SE (3.37 pp) — **FAIL**, not provisional.
Gate Zero is the only registered arm (X7 data absent; the
big-chance half of the production X9 pair is absent — possession
only, per the prereg), so there is no variant to fall back to.
C-AT2 verdict is FAIL and nothing ships; `predictions/` holds no
C-AT2 file, deliberately. The virgin-fitted params remain in
`engine/corners/fitted_params_virgin.json` as the read's record.

Reading: the virgin season's corner level fell (actual over-9.5
rate 39.0% vs 52.8% in dev; mean corners 8.99 vs 9.98) and the
model, priced off the higher dev-era levels, over-predicted
throughout (mean P(over 9.5) 46.9% vs 39.0% actual). A clean
dev pass, honestly overturned by the virgin window — the
two-stage gate working as designed.

Coordinator notes: virgin LL and calibration recomputed
independently from `engine/corners/predictions_virgin_all.csv`
(210 rows); match the harness to 6dp. Dev numbers recomputed
from `predictions_dev.csv` likewise.
