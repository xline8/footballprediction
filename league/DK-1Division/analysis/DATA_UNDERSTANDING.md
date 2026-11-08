# Data understanding — Denmark 1. Division

All figures below were measured from the JSON content for FotMob league id 85, not from the warehouse flags. The builder is `data/build_data.py`; it writes one row per finished match and two team rows per match.

## Corpus and format

| Season | rows | all-period stats | complete core splits | shotmap | referee | stats cards |
|---|---:|---:|---:|---:|---:|---:|
| 2021/2022 | 192 | 66 (34.4%) | 0 | 0 | 0 | 0 |
| 2022/2023 | 192 | 192 (100%) | 60 (31.3%) | 0 | 144 (75.0%) | 192 |
| 2023/2024 | 192 | 192 | 192 | 0 | 188 (97.9%) | 192 |
| 2024/2025 | 192 | 192 | 192 | 0 | 173 (90.1%) | 192 |
| 2025/2026 | 192 | 192 | 192 | 0 | 146 (76.0%) | 192 |
| 2026/2027 | 83 | 83 | 83 | 0 | 79 (95.2%) | 83 |

All 1,043 indexed rows are finished and were built. 2025/2026 is complete and virgin; 2026/2027 is transitional and excluded from verdicts.

There are 12 teams and exactly 192 matches in each completed season: rounds 1–22 regular (132 matches), then rounds 23–32 split into two six-team groups (30 promotion/championship and 30 relegation). The Tournament feed names distinguish those groups. No extra rounds, unfamiliar-tier ties, or playoff population exists in this corpus. Team identity is keyed by FotMob id; names are labels only.

The actual JSON has no expected-goals keys and every shotmap is empty. Goals are therefore goals-only. `touches_opp_box` is available in all-period stats for 2022/2023–2026/2027, but not 2021/2022.

## Identity and tier movers

The id↔name mapping is stable within each season; name spelling changes do not create new entities. Comparing this corpus to `DK-Superligaen/data/dk_matches.csv` finds 10 lower-tier team-seasons with a prior Superliga season (2 in each of 2022/2023–2026/2027), representing 300 prior-tier matches. The reverse comparison finds 10 Superliga team-seasons with a prior 1. Division season and another 300 prior-tier matches. This is sufficient to make an X2 mover-offset arm feasible; the offset remains estimated in Phase B, never hard-coded from these descriptive counts.
