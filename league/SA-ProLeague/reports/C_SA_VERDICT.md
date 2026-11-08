# Verdict — C-SA (Saudi Pro League corners) — **PROVISIONAL PASS** (Gate Zero ships)

Prereg: `prereg/PREREG_C_SA.md` (frozen aa3a34d, before fitting).
Dev = walk-forward scored 2023/2024 + 2024/2025 (n=612); virgin =
2025/2026 (n=306), read once for dev-passing arms (both).

## Dev (pooled LL@9.5)

| Arm | Pooled | 2023/2024 | 2024/2025 | vs baselines (league 0.7359 / naive 0.7318) |
|---|---|---|---|---|
| Gate Zero | 0.7034 | 0.7071 | 0.6997 | beats both — PASS |
| X7 | 0.6927 | 0.6973 | 0.6881 | beats both — PASS, and beats GZ in both seasons |

## Virgin 2025/2026 (n=306)

| Arm | LL@9.5 | Mean P(over) | Actual | Calibration (SE) |
|---|---|---|---|---|
| Gate Zero | 0.6961 | 0.5051 | 0.5196 | −1.45pp (2.87pp) |
| X7 | 0.6961 | 0.5051 | 0.5196 | −1.45pp (2.87pp) |
| League base rate | 0.7387 | — | — | — |
| Naive trailing-10 | 0.7289 | — | — | — |

The identical virgin rows are mechanical, not a copy error: the
architecture's per-season beta selection, fitted on prior-season
walk-forward rows for the virgin season, chose **beta = 0 for both
arms** (`active_with_nonzero_beta_share = 0.0` in
`results_virgin.json`) — with no territorial covariate active, X7
collapses to Gate Zero exactly. X7's dev edge was real but its own
selection rule switched it off for the virgin season.

Gate arithmetic: leg (i) — both 0.6961 ≤ GZ ✓ and ≤ best baseline
0.7289 ✓. Leg (ii) — |−1.45pp| > 1pp but within 1 SE (2.87pp) →
PROVISIONAL for both. Leg (iii) — X7 dev sign 2 of 2 ✓. Exact tie
on virgin LL → the prereg's tie rule ships the simpler arm.

**Ships: Gate Zero** (fitted params
`engine/corners/fitted_params_virgin.json`, gamma 0.15, r 1.145,
beta [0, 0]; predictions `predictions/c_sa_virgin_predictions.csv`,
halves via frozen 0.4740).
