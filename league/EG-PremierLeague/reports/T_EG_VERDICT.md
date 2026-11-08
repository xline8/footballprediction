# Verdict — T-EG (Egypt Premier League total shots) — **PASS** (clean; arm A ships)

Prereg: `prereg/PREREG_T_EG.md` (frozen 6b86220, before fitting).
Dev = per-match walk-forward, warm-up 2021/2022, scored
2022/2023–2024/2025 (n = 826 with target); level-layer cell tuned
on 2022/2023 (first scored season), as frozen. Virgin = 2025/2026
(n = 322), read once for all three dev-passing arms. Primary
line 22.5. Calibration = actual − predicted, as frozen.

## Dev (pooled LL@22.5)

| Arm | Pooled | 2022/2023 | 2023/2024 | 2024/2025 | vs baselines (league 0.6921 / naive 0.6783) |
|---|---|---|---|---|---|
| A (v1 pattern) | 0.6713 | 0.6867 | 0.6657 | 0.6582 | beats both — PASS |
| B (v2 level layer) | 0.6703 | 0.6867 | 0.6635 | 0.6576 | beats both — PASS |
| C (E9 trailing-r) | 0.6715 | 0.6868 | 0.6660 | 0.6585 | beats both — PASS |

Tuned on dev: lambda = 300, r_A = 43.63, level cell (120, 0.5, 50).

## Virgin 2025/2026 (n = 322)

| Arm | LL@22.5 | Calibration actual − predicted (SE) |
|---|---|---|
| **A** | **0.65757** | **−0.44pp (2.69pp)** |
| B | 0.65789 | +0.24pp (2.69pp) |
| C | 0.65764 | −0.48pp (2.69pp) |
| League base rate | 0.67851 | — |
| Naive trailing-10 | 0.66913 | — |

Gate arithmetic: reference arm = A (passed dev). Leg (i) — A
0.65757 ≤ A's own (reference) and ≤ best baseline 0.66913 ✓;
B 0.65789 > A → leg (i) FAIL; C 0.65764 > A → leg (i) FAIL
(C also fails leg (iii): dev LL ≤ A in 0 of 3 seasons). Leg (ii)
— A's calibration |−0.44pp| ≤ 1.0pp → **clean PASS**, no
provisional needed. Only A passes all legs → A ships (it is also
the lowest virgin LL outright).

**Ships: arm A** (v1 pattern; fitted params
`engine/total_shots/fitted_params_virgin.json`; predictions
`predictions/t_eg_virgin_predictions.csv`, 322 rows, halves via
frozen 0.4459).
