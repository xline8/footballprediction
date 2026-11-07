# FotMob full-response store — coverage report

Full matchDetails responses for top-5 matches, season >= 2022/23, stored under
`data_enrichment/fotmob_full/<div>/<season>/<fotmob_match_id>.json` (the store
itself is gitignored; this report and `fotmob_full_index.csv` are the committed
record). Pulled with `data_enrichment/pull_fotmob_full.py`: 12 parallel workers,
zero delay; HTTP fetches plus reuse of phase-1 raw-cache responses already on
disk; 0 fetch errors, 0 provider blocks, 0 unfetchable targets.

Targets: **7532** spine matches (season >= 2022/23, incl. played 2026/27).
Stored and indexed: **7532**.

## Per division x season (stored targets; shotmap / lineup / stats %)

| Div | Season | Targets | Shotmap % | Lineup % | Stats % |
|---|---|---|---|---|---|
| E0 | 2022/23 | 380 | 100.0% | 100.0% | 100.0% |
| E0 | 2023/24 | 380 | 100.0% | 100.0% | 100.0% |
| E0 | 2024/25 | 380 | 100.0% | 100.0% | 100.0% |
| E0 | 2025/26 | 380 | 100.0% | 100.0% | 100.0% |
| E0 | 2026/27 | 90 | 100.0% | 100.0% | 100.0% |
| SP1 | 2022/23 | 380 | 100.0% | 100.0% | 100.0% |
| SP1 | 2023/24 | 380 | 100.0% | 100.0% | 100.0% |
| SP1 | 2024/25 | 380 | 100.0% | 100.0% | 100.0% |
| SP1 | 2025/26 | 380 | 100.0% | 100.0% | 100.0% |
| SP1 | 2026/27 | 109 | 100.0% | 100.0% | 100.0% |
| D1 | 2022/23 | 306 | 100.0% | 100.0% | 100.0% |
| D1 | 2023/24 | 306 | 100.0% | 100.0% | 100.0% |
| D1 | 2024/25 | 305 | 100.0% | 100.0% | 100.0% |
| D1 | 2025/26 | 306 | 100.0% | 100.0% | 100.0% |
| D1 | 2026/27 | 72 | 100.0% | 100.0% | 100.0% |
| I1 | 2022/23 | 380 | 100.0% | 100.0% | 100.0% |
| I1 | 2023/24 | 380 | 100.0% | 100.0% | 100.0% |
| I1 | 2024/25 | 380 | 100.0% | 100.0% | 100.0% |
| I1 | 2025/26 | 380 | 100.0% | 100.0% | 100.0% |
| I1 | 2026/27 | 99 | 100.0% | 100.0% | 100.0% |
| F1 | 2022/23 | 380 | 100.0% | 100.0% | 100.0% |
| F1 | 2023/24 | 306 | 99.7% | 100.0% | 100.0% |
| F1 | 2024/25 | 306 | 100.0% | 100.0% | 100.0% |
| F1 | 2025/26 | 306 | 100.0% | 100.0% | 100.0% |
| F1 | 2026/27 | 81 | 100.0% | 100.0% | 100.0% |

Overall: shotmap 100.0%, lineup 100.0%, stats 100.0% of 7532 stored responses.

## Unfetchable

None. Every target resolved to a FotMob fixture (fixture matching was 100% in
all 25 division-season groups) and every fetch succeeded: 0 errors and 0
unfetchable targets recorded in the run checkpoint.
