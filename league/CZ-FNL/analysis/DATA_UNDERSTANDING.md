# Data Understanding — CZ FNL (FotMob 253)

The source is the read-only FotMob world warehouse, indexed by
`data_enrichment/fotmob_world_index.csv`. Filtering `league_id == 253` gives
1,311 finished rows: 240 in each complete season from 2021/2022 through
2025/2026 and 111 in 2026/2027. Every row is the single `FNL` sub-league.

FNL is a 16-club, double round-robin: 240 regular matches in a complete
season, with no split phases, playoffs, or placement matches. All 1,311 rows
are included.

| Field | Observed coverage |
|---|---:|
| Header FT score | 1,311 / 1,311 |
| Goal events | 1,311 / 1,311; event goals equal header goals in every row |
| Stats `Periods.All` | null in all 1,311 |
| SOT, corners, total shots, possession, xG | absent as target data in every row |
| Period splits | none in any row |
| Shotmap | empty in every match |
| Player stats | null in every match |
| Named referee | 0 dev matches; 0 in 2025/2026; 49/111 in 2026/2027 |

The index `has_stats=True` signal for rich-era rows is therefore a block-level
artifact: its `All` block is still null. Plain Yellow events are absent in the
dev era; 2021/2022–2024/2025 contain only YellowRed and Red card events.
From 2025/2026, plain Yellows appear (896 in that season's 240 matches).

Goals are clean and authoritative from the header. Goal event times are used
for first-half presentation only. Team identity is keyed by FotMob id. The
builder records all observed name variants and chooses the most recent name as
the canonical name; 12 ids have multiple name strings. Diacritic variants
begin in 2025/2026, while the genuine `SK Lisen` → `Artis Brno` and
`FK MAS Taborsko` → `FC Silon Taborsko` changes are retained as history.
