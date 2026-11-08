# Data understanding — Brazil Série C

The source slice is FotMob league id 8971. The completed build contains 1,286
index rows: 1,229 finished and 57 unfinished, all unfinished rows in 2021.
The score check against payload `scoreStr` is 1,229/1,229 with zero
mismatches. The unfinished 2021 rows have placeholder `0-0` index scores and
are excluded.

| season | index | finished | unfinished | first | second | final | fit set |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2021 | 206 | 149 | 57 | 127 | 20 | 2 | 147 |
| 2022 | 216 | 216 | 0 | 190 | 24 | 2 | 214 |
| 2023 | 216 | 216 | 0 | 190 | 24 | 2 | 214 |
| 2024 | 216 | 216 | 0 | 190 | 24 | 2 | 214 |
| 2025 | 216 | 216 | 0 | 190 | 24 | 2 | 214 |
| 2026 | 216 | 216 | 0 | 190 | 24 | 2 | 214 |

Payload-content coverage is the authoritative field audit. Scores exist for
all 1,229 finished matches. Stats have `stats_nonnull=0` and
`stats_value_n=0` in every row. The 2025 index `has_stats` flag is true for
215 rows and the 2026 flag for 214, but all of those blocks are
`{"Periods":{"All":null}}`: the flag lies. There are zero period splits and
zero shots in the shotmap in every season. Referee text occurs in 15/216
matches in 2025 and zero elsewhere. Lineups with 11 starters per side occur
in 216/216 matches in both 2025 and 2026, and zero matches in 2021–2024.

Events are absent in all 2021 payloads. In 2022, 193 matches contain events,
with 499 Goals and 60 Cards (38 Red, 22 YellowRed, no Yellow); 2023 has 194
event-bearing matches, 465 Goals and 78 Cards (46 Red, 32 YellowRed); 2024
has 197, 522 and 65 (36 Red, 29 YellowRed). 2025 has 216, 432 and 1,360
(1,269 Yellow, 55 Red, 36 YellowRed); 2026 has 216, 488 and 1,219
(1,155 Yellow, 35 Red, 29 YellowRed). Goal-event count equals the final score
in 215/216 matches in 2022 and 216/216 in 2023–2026. The sole gap is
4034464, 2022-10-08, Mirassol–ABC, 2–0 with zero Goal events.

The competition format is 2021: two first-phase groups of 10 (180), two
second-stage groups of four (24), and a two-leg Final (2). From 2022 onward it
is a 20-team, 19-round single first phase (190), two second-stage groups (24),
and a two-leg Final (2); in 2025–2026 the second stage is named Promotion
Round. The 2026 Final legs are dated 2026-10-17 and 2026-10-24, so 2026 is a
complete season. Team identity is FotMob ID; name-only variants include
163783 Oeste FC/Osasco Sporting and five 2025 spellings (Botafogo-PB,
Maringá, Retrô, Tombense, São Bernardo).

EDA results are recorded in `eda_summary.json` and `EDA.md`. In brief, goals
are the only populated target. The level falls from 2.417 goals/match in 2024
to 2.000 in 2025, then is 2.259 in complete 2026.
