# Verdict — C-FR (FR-Ligue2 corners)

**PASS (calibration PROVISIONAL) — Gate Zero SHIPS.**

Calibration: actual − predicted. Primary line 8.5. Prereg:
`prereg/PREREG_C_FR.md`. Dev scored n = 1,065; virgin 2025/2026
n = 306, read ONCE for the two dev-passing arms.

## Dev gate (pooled LL@8.5)

| Arm | LL@8.5 | vs base 0.7406 | vs naive 0.7332 |
|---|---:|---|---|
| Gate Zero | 0.6850 | pass | pass |
| X7 | 0.6829 | pass | pass |

X7 sign check: X7 ≤ GZ in 3/3 dev seasons (two exact ties — the
box-touch multiplier is inactive, β_bt = 0, in 2023/2024 and
2024/2025 fits).

## Virgin legs (2025/2026)

| Arm | LL@8.5 | Calibration (pp) | SE (pp) |
|---|---:|---:|---:|
| Gate Zero | 0.6852 | +2.35 | 2.84 |
| X7 | 0.6852 | +2.35 | 2.84 |
| League base rate | 0.7457 | — | — |
| Naive trailing-10 | 0.7386 | — | — |

Leg (i): 0.6852 ≤ Gate Zero's 0.6852 and ≤ best baseline 0.7386 —
PASS for both arms. The two arms' virgin predictions are identical:
in the virgin fit β_bt = 0 for X7 (and the Gate Zero covariate
betas are also 0), so the X7 construction collapses to Gate Zero,
the programme's familiar pattern.
Leg (ii): |+2.35pp| breaches the 1pp boundary by 1.35pp, within
1 SE (2.84pp) — **PROVISIONAL PASS**. The virgin ran hot on corners
(actual over-8.5 rate 56.9% vs mean predicted 54.5%).
Leg (iii): X7 sign 3/3 (see dev). Both arms pass; the tie rule
ships the simpler arm.

**Ships:** Gate Zero — `engine/corners/fitted_params_virgin.json`
(gamma 0.3, NB r 1.2061, betas 0) and
`predictions/c_fr_virgin_predictions.csv` (306 rows; FT ladder
7.5/8.5/9.5, halves presentation via the frozen 0.4803 constant).
Coordinator verification: dev harness re-run reproduced
`results_dev.json` exactly; virgin LL and calibration recomputed
from the shipped CSV — 0.6852 and +2.35pp, exact.

Defect recorded: the FR port of `gate_passes()` had its `out[arm]`
assignment dedented outside the loop (the ES original is correctly
indented), so the virgin runner initially refused Gate Zero as
"non-passing". The coordinator fixed the indentation (one line);
the gate arithmetic on the frozen dev file then read
{gate_zero: True, x7: True}, matching the hand-checked pooled LLs,
and the virgin was run once after the fix.
