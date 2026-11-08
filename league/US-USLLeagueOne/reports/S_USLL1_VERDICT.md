# S-USLL1 Verdict — USL League One shots-on-target model

Date: 2026-11-10. Prereg: `prereg/PREREG_S_USLL1.md`. Engine: `engine/sot/`.

## Verdict: FAIL — virgin calibration leg (ii); nothing ships

Both arms pass the dev gate and were read on virgin. Both beat the best
baseline on virgin LL (leg i), but both over-predict the over-8.5 rate
by ~4.5pp against an SE of ~3.4pp — outside the provisional band — so
leg (ii) fails for both and nothing ships.

## Dev results (2022–2024 regular, n=486; LL@8.5)

| Season | n | GZ | RS | League base | Naive t-10 |
|---|---:|---:|---:|---:|---:|
| 2022 | 165 | 0.669092 | 0.668192 | 0.669883 | 0.690260 |
| 2023 | 191 | 0.690221 | 0.688211 | 0.701992 | 0.685074 |
| 2024 | 130 | 0.648374 | 0.649864 | 0.723463 | 0.641934 |
| **Pooled** | **486** | **0.671854** | **0.671157** | **0.696834** | **0.675295** |

Both arms beat both baselines pooled. RS sign check vs GZ: better in
2022 and 2023, worse in 2024 → 2/3, so RS was eligible for the virgin
read alongside GZ.

## Virgin results (2025 regular, n=210)

Calibration is actual − predicted.

| Arm | LL@8.5 | Mean P(over) | Actual rate | Calibration | SE |
|---|---:|---:|---:|---:|---:|
| GZ | 0.670882 | 43.979% | 39.524% | −4.455pp | 3.371pp |
| RS | 0.670636 | 44.034% | 39.524% | −4.510pp | 3.369pp |
| League base | 0.679809 | — | 39.524% | — | — |
| Naive t-10 | 0.674164 | — | 39.524% | — | — |

Read arms: `['GZ', 'RS']`.

## Per-leg verdicts

| Leg | GZ | RS |
|---|---|---|
| Dev LL beats both baselines | PASS | PASS |
| Virgin (i) LL ≤ best baseline (0.674164) | PASS (0.670882) | PASS (0.670636) |
| Virgin (ii) calibration ≤1pp; breach ≤1 SE provisional | FAIL (4.455pp > 3.371pp SE) | FAIL (4.510pp > 3.369pp SE) |
| Virgin (iii) dev sign | n/a | PASS (2/3) |
| **Overall** | **FAIL (leg ii)** | **FAIL (leg ii)** |

The 2025 SOT level fell (8.14/match vs dev 8.55) and the model's
over-rate did not fall with it: a level-shift calibration failure, not
an LL failure.

## What ships

Nothing. The harness auto-exported a Gate Zero fallback predictions
CSV; it was removed (predictions ship for passers only). The virgin fit
record is retained for audit in `engine/sot/fitted_params_virgin.json`
(NB r=79.94); it does not ship. No predictions file.
