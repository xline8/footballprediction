# Data understanding — EE-Meistriliiga

The builder (`data/build_data.py`) audited every indexed FotMob id 248 payload
and wrote `data/ee_matches.csv`. The corpus has 1,056 unique, finished,
scored matches from 2021-03-13 through 2026-11-07.

| season | matches | rounds | teams | score | stats non-null | period splits | events | shotmap shots | referee text |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2021 | 156 | 1–32 (31–32 partial) | 10 | 156 | 0 | 0 | 150 | 0 | 0 |
| 2022 | 180 | 1–36 | 10 | 180 | 0 | 0 | 177 | 0 | 0 |
| 2023 | 180 | 1–36 | 10 | 180 | 0 | 0 | 169 | 0 | 0 |
| 2024 | 180 | 1–36 | 10 | 180 | 0 | 0 | 171 | 0 | 0 |
| 2025 | 180 | 1–36 | 10 | 180 | 0 | 0 | 180 | 0 | 61 |
| 2026 | 180 | 1–36 | 10 | 180 | 0 | 0 | 180 | 0 | 72 |

The index flags are key-presence flags and are not used as content coverage.
`content.stats.Periods` is null in all 1,056 payloads; there are no xG, stats,
or first/second-half splits. The shotmap shot list is empty everywhere. Events
are present in 1,027/1,056 matches and include goals, cards, half markers and
substitutions when supplied. Header scores are present in all 1,056.

FotMob calls the competition “Regular Season” in the warehouse, while payload
labels move from “Meistriliiga” to “Premium liiga”. Id 248 is one complete
10-team, 36-round, single round-robin competition in 2022–2026; there is no
championship or relegation split. 2021 is partial: rounds 1–30 have five
matches each, rounds 31–32 have three each, and rounds 33–36 are absent. The
season calendar is March–November.

Team identity is keyed only by FotMob id. Entrants and exits (id and observed
canonical display name) are:

- 2022: entered 49578 Tallinna Kalev; left 8694 Tulevik Viljandi.
- 2023: entered 673053 Harju Jalgpallikool; left 187946 TJK Legion.
- 2024: entered 584714 Nõmme United; left 673053 Harju Jalgpallikool.
- 2025: entered 673053 Harju Jalgpallikool; left 584714 Nõmme United.
- 2026: entered 584714 Nõmme United; left 49578 Tallinna Kalev.

Diacritic/name variants are retained as source display names but never joined
on text: ids 112484, 49578, 584714 and 828265 carry spelling variants.

Important audit discrepancy: the brief stated referee coverage was 100% in
2021–2024. In the payloads actually swept, `infoBox.Referee.text` is blank in
all 696 matches in those seasons; only 61/180 and 72/180 are populated in
2025/2026. The payload-derived result is used throughout.
