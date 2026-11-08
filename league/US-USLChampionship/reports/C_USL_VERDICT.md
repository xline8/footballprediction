# C-USL Verdict — USL Championship corners model

Date: 2026-11-09. Prereg: `prereg/PREREG_C_USL.md`. Engine: `engine/corners/`.

## Verdict: FAIL — no arm passes virgin; nothing ships

Both arms pass dev and were read on virgin. Their virgin predictions are identical because both fitted feature multipliers are zero. Neither passes virgin leg (i), so nothing ships. The ported runner auto-exported a Gate Zero fallback CSV; the coordinator removed it (predictions are shipped for passers only), so no predictions file exists for this candidate.

## Dev results (2022–2024, n=1,318; LL@9.5)

| Season | n | Gate Zero | X7 | Base rate | Naive t-10 |
|---|---:|---:|---:|---:|---:|
| 2022 | 472 | 0.685844 | 0.686047 | 0.706081 | 0.702274 |
| 2023 | 423 | 0.673455 | 0.673455 | 0.690958 | 0.688670 |
| 2024 | 423 | 0.697359 | 0.697359 | 0.728460 | 0.727411 |
| **Pooled** | **1318** | **0.685563** | **0.685636** | **0.708410** | **0.705975** |

Both arms beat both baselines. X7’s sign check is 2/3 (2022: 0.686047 > 0.685844; 2023 tie; 2024 tie), so it passes leg (iii).

X7 active/fallback composition: dev active share / active-with-nonzero-beta share were 15.466% / 15.466% (2022), 13.002% / 0% (2023), 87.470% / 0% (2024), pooled 37.785% / 5.539%.

## Virgin results (2025, n=375)

Calibration below is actual − predicted; the runner stores predicted − actual. Active/fallback shares are 97.867% / 0% for both arms.

| Arm | LL@9.5 | Mean P(over) | Actual rate | Calibration | SE |
|---|---:|---:|---:|---:|---:|
| Gate Zero | 0.684214 | 39.875% | 39.733% | −0.141pp | 2.561pp |
| X7 | 0.684214 | 39.875% | 39.733% | −0.141pp | 2.561pp |
| Base rate | 0.675548 | 35.620% | 39.733% | +4.114pp | — |
| Naive t-10 | 0.673622 | 33.936% | 39.733% | +5.798pp | — |

Read arms: `['gate_zero', 'x7']`.

## Per-leg verdicts

| Leg | Gate Zero | X7 |
|---|---|---|
| Dev gate | PASS | PASS |
| Virgin (i) LL ≤ best baseline (0.673622) | FAIL (0.684214 > 0.673622) | FAIL (0.684214 > 0.673622) |
| Virgin (ii) calibration ≤1pp; breach ≤1 SE provisional | PASS | PASS |
| Virgin (iii) dev sign | n/a | PASS (2/3) |
| **Overall** | **FAIL** | **FAIL (leg i)** |

The runner printed these gate lines verbatim:

```text
dev gate: {'gate_zero': True, 'x7': True}
virgin gate gate_zero {'leg_i': False, 'leg_ii': True, 'leg_iii': True}
virgin gate x7 {'leg_i': False, 'leg_ii': True, 'leg_iii': True}
shipped gate_zero (fallback; no arm passed)
```

## What ships

Nothing. The virgin fit record is retained for audit in `engine/corners/fitted_params_virgin.json` (gamma 0.3, r=1.244809, GZ beta [0,0], X7 beta [0], fit n=1816); it does not ship. No predictions file.
