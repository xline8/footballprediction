# Phase 1 — Data Understanding: Egypt Premier League

All measured values in this document are from analysis/eda_numbers.json, produced from the existing eg_matches.csv. The corpus has **1,545** rows. The season counts are **306, 306, 306, 225, 322, 80** for 2021/2022 through 2026/2027. The builder output was not regenerated in this phase.

## F1. Format and identity

The measured team counts are **18, 18, 18, 18, 21, 20**. Matches per team are respectively **18×34**, **18×34**, **18×34**, **18×25**, **7×26 + 14×33**, and **20×8**. The 2024/2025 split is pooled as ordinary rows; no phase feature is permitted. The warehouse has no parent tier.

## F2. Feed eras and coverage

| Season | n | stats all | half splits | shotmap | xG | touches | referee | timed goal events |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2021/2022 | 306 | 99.7% | 0.0% | 0.0% | 0.0% | 39.2% | 62.1% | 100.0% |
| 2022/2023 | 306 | 97.7% | 38.6% | 0.0% | 0.0% | 68.6% | 81.4% | 100.0% |
| 2023/2024 | 306 | 99.0% | 99.0% | 0.0% | 0.0% | 93.8% | 71.9% | 100.0% |
| 2024/2025 | 225 | 99.6% | 98.7% | 0.4% | 0.4% | 98.7% | 75.6% | 100.0% |
| 2025/2026 | 322 | 100.0% | 100.0% | 100.0% | 100.0% | 100.0% | 26.7% | 100.0% |
| 2026/2027 | 80 | 100.0% | 100.0% | 100.0% | 100.0% | 100.0% | 100.0% | 100.0% |

The xG/shotmap era therefore starts at the virgin season, 2025/2026. X1 is goals-only throughout every dev fold and in the virgin training window. X3, X4, and X6 cannot be dev-validated and are dropped.

## F3. Cards definition

The frozen target is stats-feed yellow_cards (home + away); event yellow and yellow-red columns remain audit fields. Full-feed agreement is in eda_numbers.json, including missing stats rows. The measured stats-minus-events mean is **+2.033, +3.177, +3.766, −0.032, −0.224, −0.312** by season. This confirms the feed break but does not change the frozen target.

## F4. Virgin boundary

2025/2026 is inventory-only in this phase. 2026/2027 is reserved and not read by the design evidence.
