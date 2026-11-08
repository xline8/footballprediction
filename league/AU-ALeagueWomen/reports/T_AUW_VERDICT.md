# T-AUW verdict — FAIL — nothing ships

## Dev results — pooled LL@27.5

| Arm / baseline | 2022/2023 | 2023/2024 | 2024/2025 | pooled |
|---|---:|---:|---:|---:|
| A | 0.722307 | 0.707913 | 0.671558 | 0.698179 |
| B | 0.719362 | 0.709142 | 0.674558 | 0.698950 |
| C | 0.722805 | 0.709116 | 0.670687 | 0.698417 |
| League base rate | 0.708060 | 0.694579 | 0.695666 | 0.698602 |
| Naive trailing-10 | 0.702410 | 0.724486 | 0.666610 | 0.696919 |

Gate Zero/A has pooled **0.6982**, which beats the league base **0.6986** but fails the naive baseline **0.6969**. B (**0.6990**) and C (**0.6984**) also fail. Virgin was **not read** because no arm passed the dev gate.

**Verdict: FAIL.** No virgin metrics or shipping artifacts are produced for T.
