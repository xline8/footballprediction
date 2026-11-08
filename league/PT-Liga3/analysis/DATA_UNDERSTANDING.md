# Data understanding — Portugal Liga 3

Frozen measurement date: 2026-11-10. The corpus is the FotMob world
warehouse filtered to `league_id=9112`. The index has 1,652 rows, but five
rows have an index score of `0-0` while `header.status.finished=false` and
`started=false`; the requested finished-only rule therefore produces 1,647
matches. The builder documents and asserts this payload-truth count.

## Content inventory

| season | n | stats | shotmap shots >0 | xG shots | period splits | referee named | card event | HT recoverable |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2021/2022 | 332 | 0 | 0 | 0 | 0 | 0 | 95 | 317 |
| 2022/2023 | 337 | 0 | 0 | 0 | 0 | 0 | 118 | 317 |
| 2023/2024 | 296 | 0 | 0 | 0 | 0 | 0 | 79 | 284 |
| 2024/2025 | 296 | 0 | 0 | 0 | 0 | 0 | 119 | 279 |
| 2025/2026 | 296 | 0 | 0 | 0 | 0 | 0 | 290 | 296 |
| 2026/2027 | 90 | 0 | 0 | 0 | 0 | 0 | 24 | 82 |

`content.shotmap` is present as a shell (`shots=[]`, `Periods` shell), but it
contains no shots. `content.stats` is `None` in every finished payload. No
named referee text or stats `yellow_cards` key exists. Card events exist, but
their coverage changes sharply by season and must not be interpreted as a
stable card target.

## Format and identity

Identity is FotMob team ID, never display name. B teams are retained as
separate IDs. All played phases enter one CSV table. The first two seasons
have two regular zones, promotion groups A/B, relegation groups A–D, and one
Championship Final. The finished 2021/2022 table is short by five postponed
shell rows (130 matches in each zone rather than the 132 index rows); the
2022/2023 table has 132 in each zone, 12 in each group, and one final.
2023/2024 through 2025/2026 have two 90-match zones, a 56-match promotion
group, and two 30-match relegation groups. 2026/2027 is in progress with 45
matches in each zone.

Full-time goals come from `header.teams`. Half-time goals are recovered only
from usable goal events; no half-time constant is frozen. The complete
machine-readable measurements are in `eda_summary.json`.
