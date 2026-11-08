# Data understanding — Malaysia Liga Super

The source is the FotMob world warehouse, filtered by index `league_id=8985`. The index contains 793 unique match IDs, all country Malaysia and league `Liga Super`; every indexed payload was present and finished. Payload `general.leagueName` is `Liga Super` in 499 rows and `Super Liga` in 294 rows. The builder uses the index league label for the output column.

## Format and seasons

This is one regular single table with double round-robin scheduling. There is no split group, championship/relegation round, or playoff. Complete seasons have 22 matches per team in 2021 and 2022 (12 teams), 26 in 2023 (14 teams), and 24 in 2024/2025 and 2025/2026 (13 teams). The partial 2026/2027 corpus has 12 teams and 35 matches: rounds 1–6 plus rescheduled matches labelled 13, 16, and 20.

| Season | Matches | Model rows | Teams | Dates | Rounds | Events | Lineup non-null |
|---|---:|---:|---:|---|---:|---:|---:|
| 2021 | 132 | 132 | 12 | 2021-03-05..2021-09-12 | 22 | 124 | 3 |
| 2022 | 132 | 132 | 12 | 2022-03-04..2022-10-15 | 22 | 124 | 0 |
| 2023 | 182 | 182 | 14 | 2023-02-24..2023-12-17 | 26 | 175 | 0 |
| 2024/2025 | 156 | 155 | 13 | 2024-05-10..2025-04-20 | 26 | 151 | 0 |
| 2025/2026 | 156 | 156 | 13 | 2025-08-08..2026-05-17 | 26 | 151 | 0 |
| 2026/2027 | 35 | 35 | 12 | 2026-08-21..2026-11-01 | 9 unique labels | 34 | 0 |

The calendar changes from whole calendar-year seasons in 2021–2023 to European-season labelling from 2024/2025. The 2023 season remains one whole season and is not split across analysis windows.

## Payload coverage and quirks

`content.stats` is null in 793/793 and `shotmap.shots` is empty in 793/793. Referee text is empty in 793/793. Events are present in 759/793; they contain 2,481 goals, 759 half markers, and 127 card events: 88 Red, 39 YellowRed, and 0 plain Yellow. Lineup content is non-null in 3/793. The awarded match is 4480811 (2024/2025, 2024-05-10, Johor Darul Ta'zim 3-0 Selangor, 0 events).

Team identity is the FotMob ID, not the display name. The builder writes each ID's most recent observed name. Alias map:

| ID | Names observed |
|---:|---|
| 165228 | Johor Darul Ta'zim; Johor Darul Ta'zim FC |
| 165232 | Penang; Penang FC; Pulau Pinang |
| 165233 | Kedah; Kedah Darul Aman; Kedah Darul Aman FC |
| 1124836 | Kelantan United; Kelantan DNFC; Kelantan The Real Warriors FC |
| 1783759 | Imigresen FC; Star City |
| 242698 | Sabah; Sabah FA; Sabah FC |
| 191752 | Kuala Lumpur City; Kuala Lumpur FA |
| 165234 | Sri Pahang; Sri Pahang FC |

There is only Malaysian league ID 8985 in the warehouse, so no sibling-league mover prior exists.
