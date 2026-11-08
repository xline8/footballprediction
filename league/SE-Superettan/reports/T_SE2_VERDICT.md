# Verdict — T-SE2 (SE-Superettan total shots): **FAIL (virgin leg i, all arms)**

Frozen gates: PREREG_T_SE2.md (730a5c1, before fitting). Primary line 20.5.

## Dev (warm-up 2022; scored 2023–2025, n = 710)
| Arm | LL@20.5 pooled | vs league base 0.694615 | vs naive 0.690898 |
|---|---|---|---|
| A (v1) | 0.680564 | pass | pass |
| B (v2 level layer) | 0.677984 | pass | pass |
| C (E9 trailing-r) | 0.679390 | pass | pass |
Sign check vs A: B and C each better in 2 of 3 dev seasons → leg (iii) satisfied at dev stage.

## Virgin 2026 (n = 237) — read ONCE
| Arm | LL@20.5 | Calibration | 1 SE |
|---|---|---|---|
| A | 0.719367 | +1.51pp | 3.32pp |
| B | 0.718590 | +0.26pp | 3.32pp |
| C | 0.703482 | +0.95pp | 3.28pp |
| League base rate | **0.693808** | +4.36pp | 3.24pp |
| Naive trailing-10 | 0.787479 | | |

Leg (i): EVERY arm loses to the league base rate (best arm C 0.703482 >
0.693808). FAIL for all arms, regardless of their clean/provisional
calibrations. → **FAIL; nothing ships** (shipped_arm null in
results_virgin.json; no predictions file written).

Note: the 2026 shot level fell (19.52/match, the lowest stats season) and the
per-season base-rate NB tracked the level shift better than the ratings arms.

Process note: the virgin entrypoint first halted on an inherited count assert
(== 240 stats rows; the true frozen count is 237) — corrected before any
virgin row was scored; the virgin was then read once.
