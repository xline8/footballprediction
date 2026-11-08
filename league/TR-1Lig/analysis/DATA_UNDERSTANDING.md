# TR-1Lig data understanding

The corpus was re-read from the MAIN warehouse using `league_id=165` and the
index path. It contains 1,914 index rows. The output table retains every index
row, including `header.status.awarded`; every modelling/EDA scope below filters
to finished regular, non-awarded rows.

| season | index n | regular / playoff | awarded | stats | periods | events | referee | shotmap |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2021/22 | 347 | 342 / 5 | 0 | 0 | 0 | 326 | 0 | 0 |
| 2022/23 | 347 | 342 / 5 | 29 | 0 | 0 | 299 | 0 | 0 |
| 2023/24 | 311 | 306 / 5 | 0 | 2 | 0 | 287 | 0 | 0 |
| 2024/25 | 385 | 380 / 5 | 1 | 179 | 178 | 358 | 174 | 177 |
| 2025/26 | 385 | 380 / 5 | 1 | 385 | 385 | 362 | 329 | 0 |
| 2026/27 | 139 | 139 / 0 | 0 | 139 | 139 | 139 | 138 | 0 |

Stats in 2024/25 are an Aug–Jan fragment; the February 2025 stats feed dies.
The complete 2025/26 stats season is virgin and is not evidence for a gate.
The partial 2026/27 season is reserved. Play-offs are promotion rounds `1/4`,
`1/2`, and `final` (five rows per completed season), marked `phase=playoff`.
The final has no usable Stadium/neutral signal in `infoBox`.

Monthly stats audit (index rows / rows with all-period stats):

| season-month | rows / stats |
|---|---:|
| 2024-08 | 35 / 33 |
| 2024-09 | 35 / 35 |
| 2024-10 | 30 / 30 |
| 2024-11 | 35 / 35 |
| 2024-12 | 35 / 35 |
| 2025-01 | 41 / 10 |
| 2025-02 onward in 2024/25 | 174 / 1 |
| 2025-08 through 2026-05 (2025/26) | 385 / 385 |

Awarded rows are identified only by the flag: 29 in 2022/23 (earthquake-period
administrative results), one in 2024/25, and one in 2025/26. Team identity is by
ID; name variants occur for four IDs in 2021/22, one in 2022/23, and ten in
2023/24, then none in later seasons.

## Card instrument audit

The overlap check (regular, non-awarded 2024/25 fragment + 2025/26) has n=558
rows with stats yellows. Stats and event yellows agree exactly on 2.3%; the
mean `stats - events` difference is +4.272, with stats lower in 0.0% and higher
in 97.7%. Event-yellow means are 0.000 in each pre-stats season and 0.000 in
both overlap seasons, confirming a decisive event-feed undercount rather than a
usable unified target. K-TR1 is consequently not buildable.
