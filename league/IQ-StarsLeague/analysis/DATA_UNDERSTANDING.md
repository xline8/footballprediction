# Step 1 — Data understanding: Iraq Stars League

The warehouse index has 2,032 FotMob-524 JSONs. A direct payload audit found 1,983 played matches with a numeric final score; 49 historical schedule placeholders have no payload score (13 in 2021/2022, 25 in 2022/2023, 11 in 2023/2024). The CSV therefore follows the programme's played-only rule and does not fabricate outcomes. This corrects the supplied index-count claim; payloads win.

| season | JSONs | played CSV rows | regular | playoff | dates | event rows | teams |
|---|---:|---:|---:|---:|---|---:|---:|
| 2021/2022 | 380 | 367 | 367 | 0 | 2021-09-20–2022-07-03 | 0 | 20 |
| 2022/2023 | 380 | 355 | 355 | 0 | 2022-10-09–2023-07-21 | 0 | 20 |
| 2023/2024 | 383 | 372 | 369 | 3 | 2023-10-26–2024-07-23 | 0 | 20 |
| 2024/2025 | 380 | 380 | 380 | 0 | 2024-09-20–2025-07-04 | 315 | 20 |
| 2025/2026 | 379 | 379 | 379 | 0 | 2025-09-13–2026-06-02 | 352 | 20 |
| 2026/2027 | 130 | 130 | 130 | 0 | 2026-08-14–2026-11-08 | 116 | 20 |

The competition is a 20-team, 38-round, 10-match-per-round double round-robin on an August–July calendar. The 2023/2024 playoff rows are rounds `1/2` (two matches on 2024-07-19) and `final` (2024-07-23), after round 38. The phase rule keys only on `general.matchRound`; `content.hasPlayoff` is not reliable here.

Observed turnover by season: 2022/2023 adds Al Hedood, Duhok, and Karbalaa; 2023/2024 adds Al Minaa and Amanat Baghdad; 2024/2025 adds Al-Karma and Diyala; 2025/2026 adds Al-Gharraf, Al-Mosul, and Amanat Baghdad. Team ids are the state key; the payload audit found no stable id with a changed display name in these rows.

Coverage across all 2,032 JSONs, measured from payloads: `content.stats` is null 2,032/2,032; shotmap shots are empty 2,032/2,032; lineup is null 2,032/2,032; referee text is empty 2,032/2,032. Thus there are no SOT, corners, total shots, xG, stats cards, referees, lineups, or period splits.

Events are absent in the first three seasons and present in 315/380, 352/379, and 116/130 payloads in the last three seasons. The event feed contains goals, red-card variants, and half markers; it contains no yellow-card target. The 2025/2026 inventory quirk is round 32 with nine matches: Al Kahrabaa–Al Najaf was not played. No virgin outcome statistic is computed here.
