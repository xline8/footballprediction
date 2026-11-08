# Verdict — C-MA (Morocco Botola Pro corners)

**FAIL at the virgin LL leg. Nothing ships.**

Prereg: `prereg/PREREG_C_MA.md`. Dev = rich-era scored window
2025-01-01 – 2025-05-12 (n=109); virgin = 2025/2026 (n=226), read
ONCE for Gate Zero (the only arm), which passed dev. All numbers
recomputed by the coordinator from `predictions_dev.csv` /
`predictions_virgin.csv`; arm numbers match the engine JSON
exactly. Calibration = actual − predicted.

## Dev LL @ 8.5 (n=109)

| arm / baseline | LL@8.5 |
|---|---|
| Gate Zero (possession-only v3) | **0.6998** |
| league base rate | 0.7306 |
| naive trailing-10 | 0.7037 |

Gate Zero beats both baselines → dev PASS (the naive margin is
0.004, recorded as narrow).

## Virgin (2025/2026, n=226)

| arm / baseline | LL@8.5 | mean P(over 8.5) |
|---|---|---|
| Gate Zero | 0.6792 | 0.3967 |
| league base rate | 0.6920 | 0.4980 |
| naive trailing-10 | **0.6615** | 0.3220 |

Actual over-rate 0.3584; actual mean total 7.58 vs model mean
7.92 (the virgin season's corner level fell versus the dev era).

Virgin legs: (i) LL — the arm's LL must be ≤ the best baseline's:
0.6792 > 0.6615 (naive) → **LL leg FAILS**. (ii) Calibration —
actual − mean predicted = −3.83pp, SE 3.28pp: the breach exceeds
1pp but lies within 1 SE of the boundary, so this leg alone would
have been PROVISIONAL PASS. It is moot: leg (i) already fails.
C-MA verdict is FAIL; nothing ships (the pre-written shipped
predictions file was deleted, not committed).

## Defect (stated plainly)

The virgin harness's pre-virgin fit used all 172 stats-bearing
2024/2025 rows, including 8 sporadic rich payloads dated before
the frozen rich-era boundary of 2024-11-01, which PREREG_C_MA's
era rule excludes from state. The deviation is small (8 of 172
training rows, all genuinely stats-bearing) and it advantaged the
model, not the baselines' gate arithmetic on the virgin itself;
the LL-leg failure margin (0.0177) is far larger than any
plausible effect of 8 training rows. No re-run was performed —
re-running after a virgin failure to chase a pass is exactly what
the frozen rules forbid. Recorded for any future prereg.

Fitted params (`fitted_params_virgin.json`: gamma 0.15, r 1.0502,
possession beta 0.005, fit_n 159) are retained as evidence only.
Production code untouched.
