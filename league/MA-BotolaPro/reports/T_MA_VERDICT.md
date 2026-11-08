# Verdict — T-MA (Morocco Botola Pro total shots)

**FAIL at the virgin LL and calibration legs. Nothing ships.**

Prereg: `prereg/PREREG_T_MA.md`. Dev = rich-era scored window
2025-01-01 – 2025-05-12 (n=109); virgin = 2025/2026 (n=226), read
ONCE for arm A only (see dev table). All numbers recomputed by
the coordinator from `predictions_dev.csv` /
`predictions_virgin.csv`; they match the engine JSON exactly.
Calibration = actual − predicted.

## Dev LL @ 16.5 (n=109)

| arm / baseline | LL@16.5 |
|---|---|
| A (v1 pattern) | **0.6850** |
| B (v2 level layer) | 0.6852 |
| C (E9 trailing-r) | 0.6929 |
| league base rate | 0.7005 |
| naive trailing-10 | 0.6890 |

A and B both beat both baselines on dev; C loses to naive and is
dead. Under the prereg's mechanical reading, the variant sign
check requires B's dev LL ≤ A's: 0.6852 > 0.6850 → B is not a
passing arm and was NOT read on the virgin. A alone was read.

## Virgin (2025/2026, n=226) — arm A

| arm / baseline | LL@16.5 | mean P(over 16.5) |
|---|---|---|
| A | 0.7147 | 0.5125 |
| league base rate | **0.6931** | 0.5001 |
| naive trailing-10 | 0.7081 | 0.5725 |

Actual over-rate 0.6062; actual mean total 17.87 vs model mean
17.44.

Virgin legs: (i) LL — A's 0.7147 exceeds BOTH baselines' (best
0.6931) → **LL leg FAILS**. (ii) Calibration — actual − mean
predicted = **+9.37pp**, SE 3.35pp: far beyond 1pp and beyond
1 SE of the boundary → **calibration leg FAILS** outright. The
virgin season's shot level jumped (mean 17.87 vs dev-era 15.99;
over-16.5 rate 0.606 vs 0.468) and arm A's probabilities did not
follow. T-MA verdict is FAIL; nothing ships (the pre-written
shipped predictions file was deleted, not committed).

## Defect (stated plainly)

Same virgin-harness deviation as C-MA: the pre-virgin fit used
all 172 stats-bearing 2024/2025 rows, including 8 dated before
the frozen 2024-11-01 rich-era boundary that PREREG_T_MA
excludes from state. It advantaged the model and cannot explain
a failure of this size (+9.37pp calibration, LL worse than both
baselines). No re-run was performed, per the frozen rules.
Recorded for any future prereg.

Fitted params (`fitted_params_virgin.json`: lambda 3.0,
r_A 12.516) are retained as evidence only. Production code
untouched.
