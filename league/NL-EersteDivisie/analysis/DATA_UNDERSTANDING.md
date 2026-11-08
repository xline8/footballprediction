# NL Eerste Divisie — data understanding

Phase 1 uses FotMob league id 111 and filters `general.leagueName == "Eerste Divisie"`. The warehouse index contains 2,039 rows: 380 in each of 2021/2022–2025/2026 and 139 in 2026/2027. Every selected row is a finished regular-season match, with rounds 1–38 in the completed seasons and rounds 1–14 in the partial season. There are no nacompetitie/play-off rows in this feed; no exclusion count is invented.

| season | matches | score | all stats | period splits | events | referee text | xG key | touches opp box | shotmap |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2021/2022 | 380 | 100% | 100% | 26.3% | 100% | 47.4% | 0% | 72.1% | 0 |
| 2022/2023 | 380 | 100% | 100% | 25.8% | 100% | 100.0% | 0% | 77.6% | 0 |
| 2023/2024 | 380 | 100% | 100% | 100.0% | 100% | 95.8% | 0% | 85.3% | 1 |
| 2024/2025 | 380 | 100% | 100% | 100.0% | 100% | 99.5% | 0% | 100.0% | 0 |
| 2025/2026 | 380 | 100% | 100% | 100.0% | 100% | 89.5% | 0% | 100.0% | 0 |
| 2026/2027 | 139 | 100% | 100% | 100.0% | 100% | 100.0% | 0% | 100.0% | 0 |

All 2,039 rows have stats and events. `expected_goals` is absent throughout, and the shotmap is absent apart from one row; builder shotmap/xG columns are retained as zero/NaN. The referee field is not complete, especially in 2021/2022, so referee-based work must be coverage-aware. `touches_opp_box` becomes complete in 2024/2025 and 2025/2026 but is partial earlier.

The competition format represented here is 20 teams and 38 regular-season rounds. Promotion/relegation and the real-world nacompetitie exist in the Dutch pyramid, but the feed supplied here contains regular-season rows only and no play-off rows. The parent tier is NL Eredivisie, FotMob id 57. Reserve sides observed in the feed are Jong Ajax, Jong PSV, Jong FC Utrecht, and Jong AZ Alkmaar; they are not treated as ordinary promotion/relegation movers.

The exact reproducible inventory is in `inventory_summary.json`; the script is `inventory.py`.
