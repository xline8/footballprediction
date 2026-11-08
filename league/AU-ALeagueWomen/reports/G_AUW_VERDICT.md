# G-AUW verdict — FAIL — nothing ships

## Dev results — pooled LL@2.5, 1X2 LL and RPS

Gate Zero: OU2.5 LL **0.7298** vs league **0.6966**, 1X2 LL **1.0917** vs **1.0587**, RPS **0.2426** vs **0.2402**. SHRINK is identical/degenerate. The Gate Zero dev gate fails. Virgin was **not read** because the frozen rule requires a dev-passing Gate Zero before virgin evaluation.

| Arm / baseline | 2022/2023 | 2023/2024 | 2024/2025 | pooled |
|---|---:|---:|---:|---:|
| Gate Zero | 0.784003 | 0.690803 | 0.728339 | 0.729846 |
| SHRINK | 0.784003 | 0.690803 | 0.728339 | 0.729846 |
| League base rate | 0.709254 | 0.677425 | 0.705764 | 0.696563 |
| Naive trailing-10 | 1.001195 | 1.092872 | 1.015928 | 1.039500 |

**Verdict: FAIL.** No virgin metrics or shipping artifacts are produced for G.
