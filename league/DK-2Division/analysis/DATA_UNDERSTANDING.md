# Data understanding — Denmark 2. Division

All figures were measured from FotMob JSON content for league 239. The builder writes one row per finished match; team identity is keyed by FotMob id.

| Season | rows | goals | stats | shotmap shots | events empty | HT-paired | referee |
|---|---:|---:|---|---:|---:|---:|---:|
| 2021/2022 | 192 | 523 | 61 shells, otherwise null | 0 | 10 | 182 | 0 |
| 2022/2023 | 192 | 566 | null | 0 | 33 | 159 | 0 |
| 2023/2024 | 192 | 572 | null | 0 | 5 | 187 | 0 |
| 2024/2025 | 192 | 487 | null | 0 | 7 | 185 | 0 |
| 2025/2026 | 192 | 533 | null | 0 | 12 | 180 | 0 |
| 2026/2027 | 90 | 262 | null | 0 | 4 | 86 | 0 |

Scores are complete. The 2022/2023 event feed is incomplete: goal events are 479 versus 566 score-implied goals and 33 matches have empty events. Card events are reds only (19–27 per season; zero usable yellow-card target). `playerStats` is null everywhere. Referee text is empty in all 1,050 payloads. Names vary; ids are stable.

The fixture graph has 12 teams. Rounds 1–22 are regular: one 12-team component, 66 pair edges, 132 matches. Rounds 23–32 are split: two six-team components, 30 pair edges, 60 matches. `hasPlayoff` has no playoff population. 2026/2027 is through round 15.

| Season | DK-1 → DK-2 | DK-2 → DK-1 |
|---|---|---|
| 2022/2023 | Esbjerg fB; Jammerbugt FC | Hillerød; Næstved |
| 2023/2024 | Fremad Amager; Nykøbing FC | B 93; Kolding IF |
| 2024/2025 | FC Helsingør; Næstved | FC Roskilde; Esbjerg fB |
| 2025/2026 | FC Roskilde; Vendsyssel FF | Aarhus Fremad; Middelfart |
| 2026/2027 | B 93; Middelfart | AB; Vendsyssel FF |

There are 10 DK-1-to-DK-2 mover team-seasons, two per season, with prior-tier matches in the warehouse. The other two entrants come from the unwarehoused 3rd Division.
