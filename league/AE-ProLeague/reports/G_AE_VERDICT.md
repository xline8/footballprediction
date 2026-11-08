# Verdict — G-AE (AE-ProLeague goals)

**FAIL at the dev gate. Virgin 2025/2026 deliberately NOT read.**
Nothing ships.

Dev (walk-forward, scored 2022/2023–2024/2025, n=545; recomputed
exactly from `engine/goals/predictions_dev.csv`):

| Arm | 1X2 LL | RPS | OU2.5 LL | Climatology 1X2 / RPS / OU |
|---|---|---|---|---|
| Gate Zero | 0.995584 | 0.207591 | **0.691547** | 1.078718 / 0.238450 / **0.666376** |
| SHRINK | 0.995584 | 0.207591 | **0.691547** | (same) |

Gate arithmetic: Gate Zero beats climatology on 1X2 LL and RPS but
**loses the OU2.5 leg** (0.691547 > 0.666376) → the dev gate fails →
per the frozen rule the variants are moot and the virgin is not read.
SHRINK is identical to Gate Zero pooled (it differs only in the
2022/2023 fold, where its OU LL is worse, 0.723539 vs Gate Zero's
fold value). The program's binding constraint holds here too: the DC
1X2 signal is real, the OU2.5 total is not separable from the base
rate in this league.
