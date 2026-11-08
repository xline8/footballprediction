# C-USLL1 Verdict — USL League One corners model

Date: 2026-11-10. Prereg: `prereg/PREREG_C_USLL1.md`. Engine: `engine/corners/`.

## Verdict: PASS (provisional) — Gate Zero ships

Gate Zero passes dev and virgin; its virgin calibration breach
(+1.49pp) is within 1 SE, so the pass is provisional. The X7 box-touch
arm fails its dev gate outright — driven by a 2024 blow-up — and was
not read on virgin.

## Dev results (2022–2024 regular, n=486; LL@9.5)

| Season | n | Gate Zero | X7 | Base rate | Naive t-10 |
|---|---:|---:|---:|---:|---:|
| 2022 | 165 | 0.674103 | 0.666875 | 0.671187 | 0.675017 |
| 2023 | 191 | 0.686397 | 0.689600 | 0.707592 | 0.696601 |
| 2024 | 130 | 0.694546 | 0.811961 | 0.701134 | 0.703501 |
| **Pooled** | **486** | **0.684403** | **0.714615** | **0.693505** | **0.691119** |

X7 active/fallback composition (both-teams-active share / with nonzero
beta): 2022: 1.212% / 0%; 2023: 1.571% / 1.571%; 2024: 65.385% /
65.385%. The arm was nearly dormant while box-touch coverage was thin,
then activated in 2024 — the first season its trailing features were
mostly present — and produced the worst single-season LL in this
league's build (0.811961 against a 0.701134 base rate). The box-touch
multiplier fitted on the short covered history does not transfer.

## Virgin results (2025 regular, n=210)

Calibration is actual − predicted.

| Arm | LL@9.5 | Mean P(over) | Actual rate | Calibration | SE |
|---|---:|---:|---:|---:|---:|
| Gate Zero | 0.688533 | 42.320% | 43.810% | +1.490pp | 3.441pp |
| Base rate | 0.697479 | 36.262% | 43.810% | +7.548pp | — |
| Naive t-10 | 0.714435 | 34.490% | 43.810% | +9.320pp | — |

Read arms: `['gate_zero']`.

## Per-leg verdicts

| Leg | Gate Zero | X7 |
|---|---|---|
| Dev gate (beats both baselines) | PASS (0.684403) | FAIL (0.714615 > 0.691119) |
| Virgin (i) LL ≤ best baseline (0.697479) | PASS (0.688533) | not read |
| Virgin (ii) calibration ≤1pp; breach ≤1 SE provisional | PROVISIONAL PASS (1.490pp ≤ 3.441pp SE) | not read |
| Virgin (iii) dev sign | n/a | n/a |
| **Overall** | **PASS (provisional)** | **FAIL (dev gate)** |

## What ships

Gate Zero. Fitted params: `engine/corners/fitted_params_virgin.json`
(gamma 0.15, r=1.107166, beta [0, 0] — the fitted territorial
multiplier is zero, so the shipped model is the ratings+NB core;
fit n=643). Predictions: `predictions/c_usll1_virgin_predictions.csv`
(210 rows; virgin LL and calibration recomputed independently from
this CSV by the coordinator — exact match; halves at the frozen
0.469 share).
