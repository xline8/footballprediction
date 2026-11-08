# Exploratory data analysis

All results are descriptive and were computed without model fitting. Charts
are generated from `eda_summary.json`.

| season | n | goals | home | away | event yellows | all Card events |
|---|---:|---:|---:|---:|---:|---:|
| 2021/2022 | 332 | 2.536 | 1.370 | 1.166 | 0.000 | 0.352 |
| 2022/2023 | 337 | 2.478 | 1.365 | 1.113 | 0.000 | 0.460 |
| 2023/2024 | 296 | 2.486 | 1.321 | 1.166 | 0.007 | 0.341 |
| 2024/2025 | 296 | 2.375 | 1.328 | 1.047 | 1.024 | 1.270 |
| 2025/2026 | 296 | 2.230 | 1.193 | 1.037 | 4.078 | 4.338 |
| 2026/2027 | 90 | 2.578 | 1.411 | 1.167 | 0.289 | 0.500 |

The card-event break is a coverage break, not a measured regime change.

Career-pooled chronological split-half, ratio-of-sums team-match rates, gives
goals-for r=0.440 and goals-against r=0.564 across 42 teams. Event-yellow-for
is r=0.328 across 42 teams and is supplementary event-source evidence only;
it is not stats-yellow reliability. SOT, corners, and total shots have no
valid observations.

Half-time goals are recoverable for 1,575/1,647 matches; the descriptive
all-match 1H goal share over recoverable matches is 0.4366. No halves constant
is frozen and presentation remains FT-only.

PT/PT2 CSVs were absent from this worktree, so the cross-tier check uses the
same indexed payload source for league IDs 61, 185, and 9112; this limitation
is recorded in `eda_summary.json`. Direct Liga Portugal ↔ Liga 3 counts are
zero in every transition. Liga 3 ↔ Liga Portugal 2 counts (PT2 → Liga 3 /
Liga 3 → PT2) are 2/2, 2/3, 2/2, 1/2, and 2/2 for destination seasons
2022/2023 through 2026/2027. Counts are too small for a frozen mover offset.

Named-referee coverage is 0/1,647 (0%) in every season. Cards stats-vs-events
validation is not estimable: stats yellow availability is 0 and validation
n=0. Per-season phase counts and all coverage fields are in the summary.
