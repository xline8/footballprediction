# Verdict — C-EG (Egypt Premier League corners) — **PROVISIONAL PASS** (Gate Zero ships)

Prereg: `prereg/PREREG_C_EG.md` (frozen 6b86220, before fitting).
Dev = scored 2022/2023–2024/2025 (n = 826 with target), warm-up /
training history from 2021/2022. Virgin = 2025/2026 (n = 322),
read once for both dev-passing arms. Primary line 8.5.
Calibration = actual − predicted, as frozen.

## Dev (pooled LL@8.5)

| Arm | Pooled | 2022/2023 | 2023/2024 | 2024/2025 | vs baselines (league 0.7362 / naive 0.7437) |
|---|---|---|---|---|---|
| Gate Zero | 0.6905 | 0.6903 | 0.6905 | 0.6908 | beats both — PASS |
| X7 | 0.6855 | 0.6822 | 0.6849 | 0.6908 | beats both — PASS |

X7's dev sign check vs Gate Zero: ≤ in 3 of 3 seasons ✓ (equal in
2024/2025).

## Virgin 2025/2026 (n = 322)

| Arm | LL@8.5 | Calibration actual − predicted (SE) |
|---|---|---|
| Gate Zero | 0.6938 | +1.82pp (2.79pp) |
| X7 | 0.6938 | +1.82pp (2.79pp) |
| League base rate | 0.7431 | — |
| Naive trailing-10 | 0.7563 | — |

Gate arithmetic: on the full-dev virgin fit, X7's territorial
coefficient fitted to exactly **beta = 0.0**, so X7's virgin
predictions are numerically identical to Gate Zero's (its dev
edge came from the earlier folds' fits). Leg (i) — both arms
0.6938 ≤ best baseline 0.7431 ✓. Leg (ii) — calibration +1.82pp
breaches the 1.0pp boundary but lies within 1 SE (2.79pp) →
PROVISIONAL for both. Leg (iii) — X7 ✓ (3 of 3). Both-pass rule
with an exact virgin-LL tie → the simpler arm ships.

**Ships: Gate Zero** (fitted params
`engine/corners/fitted_params_virgin.json`; predictions
`predictions/c_eg_virgin_predictions.csv`, 322 rows, halves via
frozen 0.4604). X7 ships nothing extra: in the shipped (virgin)
fit it is Gate Zero with a zero coefficient.
