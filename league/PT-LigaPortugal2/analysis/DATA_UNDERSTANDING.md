# Data understanding — Portugal Liga Portugal 2

Frozen measurement date: 2026-11-09. The corpus is the FotMob world
warehouse, index filtered to `league_id=185`, with payload checks performed
on the JSON content. There are 1,619 finished matches: 306 in each of
2021/2022 through 2025/2026 and 89 in 2026/2027.

## Content inventory

| season | n | stats | xG key | period splits | shotmap shots >0 | referee named | card event | lineup |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2021/2022 | 306 | 0 | 0 | 0 | 0 | 0 | 113 | 83 |
| 2022/2023 | 306 | 0 | 0 | 0 | 0 | 0 | 83 | 24 |
| 2023/2024 | 306 | 0 | 0 | 0 | 0 | 0 | 62 | 1 |
| 2024/2025 | 306 | 90 | 0 | 0 | 0 | 0 | 140 | 95 |
| 2025/2026 | 306 | 306 | 0 | 0 | 0 | 0 | 303 | 306 |
| 2026/2027 | 89 | 0 | 0 | 0 | 0 | 0 | 17 | 18 |

The 90 stats matches in 2024/2025 are the only partial stats block. The
2025/2026 stats block is complete. Its available `All` keys are
`BallPossesion`, `total_shots`, `ShotsOnTarget`, and `corners`; there is no
`expected_goals` or `yellow_cards` key. The shotmap is present as an empty
shot list in every payload. Referee text is empty in all 1,619 payloads.

## Format and identity

The first five seasons are 18-team double round robins (306 matches each,
one match per unordered pair at each venue). The 2026/2027 pull has 18
distinct team IDs and 89 played matches and is in progress. The calendar is
the usual August–May split-season label.

Identity is keyed by FotMob team ID, never by display name. Name variants
include accented/unaccented Portuguese names and B teams: Benfica B and FC
Porto B occur throughout, Sporting CP B occurs in 2025/2026–2026/2027, and
CF Os Belenenses appears in 2023/2024. The payload also contains occasional
lineup objects; presence counts above measure a non-empty `content.lineup`,
not lineup completeness.

Goals and half-time goals are separate: full-time scores come from the
header, while half-time scores are recovered from goal events when the event
list is sufficient. Half-time goals are recoverable for 1,540/1,619 matches;
the remaining 79 have no usable event-derived half-time score.

The complete machine-readable measurements are in `eda_summary.json`.
