# Phase 1 — Data Understanding: FotMob Brazil Série B

Source: FotMob world warehouse, `league_id = 8814`, indexed by
`data_enrichment/fotmob_world_index.csv`. The builder reads JSONs from the
main checkout through `MAIN_REPO` and writes the two analysis CSVs.

## Integrity and format

The slice contains 2,270 finished rows: 380 each in 2021–2025 and 370 in
2026. All parse, are unique, and have FT scores. There are 20 teams and
rounds 1–38 only. `hasPlayoff` is absent/`None` in every payload; no playoff
or split phase exists. This verifies the coordinator's format facts.

| season | n | All stats | half splits | xG stats | shotmap | box touches | referee |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2021 | 380 | 100% | 0.3% | 1 | 1 | 26.8% | 0% |
| 2022 | 380 | 100% | 0% | 0 | 0 | 27.9% | 94.7% |
| 2023 | 380 | 100% | 99.7% | 0 | 0 | 63.9% | 93.7% |
| 2024 | 380 | 100% | 100% | 0 | 0 | 100% | 76.6% |
| 2025 | 380 | 100% | 100% | 100% | 100% | 100% | 87.1% |
| 2026 partial | 370 | 100% | 99.7% | 369 | 370 | 99.7% | 49.5% |

The xG era therefore starts in the virgin 2025 season itself. This is the
important Série B contradiction to the Série A template: xG is not a dev-era
input. The coordinator's coverage counts agree, apart from the harmless
rounding of 2021's one covered match and the exact 2026 referee count.

## Cards definition investigation

Event card counts by season were: 2021 `Yellow=0, Red=46, YellowRed=43`; 2022
`Yellow=0, Red=61, YellowRed=34`; 2023 `Yellow=2,057, Red=73, YellowRed=39`;
2024 `Yellow=2,015, Red=70, YellowRed=49`. The 2021–2022 event stream cannot
recover ordinary yellows. The stats-feed yellow mean/match is 1.195 and
1.203 in those seasons, versus 5.061 and 5.111 in 2023–2024. Individual
payloads show stats values even when the event stream has no ordinary-yellow
records; lineup performance events are player-level and are not a complete,
stable match target. Conclusion: **2021–2022 cards are unusable from both
sources**. The target is stats-feed yellows from 2023 onward, with explicit
`None` and `unusable_pre2023` before that.

## Movers

The index verifies four Série A and four Série C presence movers into Série B
at every 2022–2026 transition. Série C has 206 rows in 2021 and 216 thereafter,
so only presence—not its competition format—is used. The transition sets are
recorded in EDA and are used only as pre-season labels in the X2 arm.
