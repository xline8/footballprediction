# Data understanding — MK-PrvaLiga

The source is the FotMob world warehouse, filtered by index `league_id=249` and checked against each payload. The corpus has 1,022 finished matches from 2021/2022 through the partial 2026/2027 season. Every payload has `general.leagueName=Prva Liga`, `parentLeagueId=249`, a parseable `scoreStr`, and `finished=true`.

## Format and coverage

This is one regular single table. All rounds are in scope; no split group, championship/relegation round, or playoff is present. The seasons have 33 rounds except the in-progress 2026/2027 season, which currently has rounds 1–13. Team counts are 12, 11, 12, 12, 12, and 10. Match counts are 198, 165, 198, 198, 198, and 65.

`content.stats` is null and `content.shotmap.shots` is empty in 1,022/1,022 payloads. No xG is present. Referee text is empty in 1,022/1,022. Lineup is non-null in 4 payloads; three are `unavailable` stubs and one is a `standard` lineup. Events are present in 919/1,022 matches. The event feed contains Goal, Half, and Card types. Card events contain 131 Red and 87 YellowRed events and zero plain Yellow events. There are 103 event-less matches.

| Season | Matches | Model rows | Teams | Dates | Events | Stats | Shotmap | Referee | Lineup non-null |
|---|---:|---:|---:|---|---:|---:|---:|---:|---:|
| 2021/2022 | 198 | 198 | 12 | 2021-08-08..2022-05-15 | 179 | 0 | 0 | 0 | 0 |
| 2022/2023 | 165 | 165 | 11 | 2022-08-06..2023-05-14 | 151 | 0 | 0 | 0 | 1 |
| 2023/2024 | 198 | 198 | 12 | 2023-08-06..2024-05-18 | 179 | 0 | 0 | 0 | 0 |
| 2024/2025 | 198 | 186 | 12 | 2024-08-11..2025-05-18 | 165 | 0 | 0 | 0 | 0 |
| 2025/2026 | 198 | 197 | 12 | 2025-08-08..2026-05-25 | 184 | 0 | 0 | 0 | 3 |
| 2026/2027 | 65 | 65 | 10 | 2026-07-24..2026-11-08 | 61 | 0 | 0 | 0 | 0 |

## Quirk register

- 2022/2023 is an 11-team triple round-robin season: 165 matches.
- 2026/2027 is a 10-team, 65-match season and remains an untouched reserve.
- There are 13 awarded matches. Nine are unplayed walkovers, three were played then overturned, and one is unplayed. They remain in the CSV with `is_awarded=1` and are excluded from every fit and score.
- Team identity is FotMob ID, not display name. ID 769984 changes from FC Academy Pandev to AP Brera Strumica; 7867 has Bregalnica Stip/Štip; 276798 has Makedonija GjP/GP variants.
- Goal-event counts reproduce official scores for all non-awarded matches. Goal-time first-half derivation agrees with the Half event in 919/919 eventful matches.
- The complete North Macedonia index contains only league ID 249, so no sibling MK league is available for mover priors.
