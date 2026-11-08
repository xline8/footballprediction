# T-BRB verdict — FAIL — nothing ships

Primary line 26.5; dev n=1,140 and virgin 2025 n=380. Calibration is ACTUAL − PREDICTED.

## Dev results

| Arm / baseline | LL@26.5 | Sign vs A |
|---|---:|---:|
| A | 0.68168 | — |
| B | 0.68207 | 1/3 |
| C | 0.68155 | 3/3 |
| League base rate | 0.69117 | — |
| Naive | 0.69024 | — |

All three arms pass dev.

## Virgin results

| Arm / baseline | LL@26.5 | Calibration pp | SE pp |
|---|---:|---:|---:|
| A | 0.673529 | −4.126 | 2.506 |
| B | 0.673088 | −3.536 | 2.507 |
| C | 0.674696 | −4.542 | 2.507 |
| League base rate | 0.697504 | −7.094 | 2.550 |
| Naive | 0.682541 | −1.861 | 2.533 |

## Gate arithmetic

- Leg (i): reference A; A and B are at or below the reference and best baseline, while C is above A and fails the reference comparison.
- Leg (ii): A, B, and C fail calibration, including the one-SE allowance: their absolute breaches 4.126, 3.536, and 4.542pp exceed 1+SE (3.506, 3.507, 3.507pp).
- Leg (iii): B fails at 1/3; C passes at 3/3, but this is moot because no arm clears leg (ii).

No arm passes; no fitted virgin parameters or predictions ship.
