# Exploratory data analysis

All figures are recomputed from eligible `wal_matches.csv`; exact values are in `eda_numbers.json`.

| season | n | goals/match | H | D | A | O2.5 | BTTS |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2021/2022 | 192 | 2.938 | .411 | .234 | .354 | .500 | .458 |
| 2022/2023 | 192 | 3.073 | .505 | .182 | .312 | .583 | .516 |
| 2023/2024 | 192 | 2.948 | .417 | .224 | .359 | .547 | .500 |
| 2024/2025 | 192 | 3.010 | .448 | .203 | .349 | .604 | .583 |
| 2025/2026 | 192 | 2.896 | .359 | .260 | .380 | .542 | .505 |
| 2026/2027 | 127 | 3.323 | .488 | .142 | .370 | .614 | .496 |

F1 levels/drift: the 2026/27 partial rate is not a level-shift claim; it is n=127 under the 16-team expansion. F2 team traits are reliable: GF/GA split-half r are 0.702/0.862, 0.826/0.759, 0.780/0.598, 0.666/0.812 and 0.495/0.453 (per-team chronological odd/even split, keyed by team id so mid-season renames do not split a club in two). F3 halves are frozen: pooled first-half goals are 1,456/3,276 = 0.4444; observed variance 0.10565 versus binomial floor 0.10794, excess about −0.0023. F4 movers are the incoming list in `eda_numbers.json`; there is no Welsh sibling prior, so X2 is unavailable. F13 confirms all SOT/corners/cards/xG/total-shots coverage is absent.

The 2026/27 expansion is a regime note, not evidence of hotter long-run scoring. The static band check finds zero teams with 1–5 prior in-league matches in any dev/virgin fold, so SHRINK is expected to be a no-op (to be verified by the dev harness's changed-rows count).
