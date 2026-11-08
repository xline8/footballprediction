# Phase 1 — Data Understanding: Faroe Islands Premier League

Corpus: FotMob world warehouse, league id 250, seasons 2021–2026. The
index contains 810 rows and the payload path for every row resolves. Dates
run from 2021-03-06 through 2026-10-31. The regular-season format is stable:
10 clubs, rounds 1–27, and a triple round robin (135 matches per season).
There is no split group, championship/relegation round, or playoff.

## Coverage

The matrix below is measured from payload content, not just index flags.
`events/cards` means that the matchFacts event list is present and includes
the event feed used for goals and cards. Stats and shotmap are shown as
content coverage; their keys exist but their useful contents do not.

| season | n | score | stats | period splits | events/cards | referee text | shotmap/xG |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2021 | 135 | 100% | 0% | 0% | 100% | 0% | 0% |
| 2022 | 135 | 100% | 0% | 0% | 100% | 0% | 0% |
| 2023 | 135 | 100% | 0% | 0% | 100% | 0% | 0% |
| 2024 | 135 | 100% | 0% | 0% | 100% | 0% | 0% |
| 2025 | 135 | 100% | 0% | 0% | 100% | 0% | 0% |
| 2026 | 135 | 100% | 0% | 0% | 100% | 0% | 0% |

The `content.stats` section is absent/null for all 810 payloads, and all have
an empty shot list. All have a `Half` event at time 45 with stored
home and away scores. All have a lineup, but lineups are not used: R6 is
closed. The referee key exists in all payloads, but its text is empty in all
810. Events contain 2,673 goals, 1,620 half markers, 3,265 cards (3,116
Yellow, 75 YellowRed, 74 Red), 5,437 substitutions, and 21 MissedPenalty
events.

## Team identity and names

All joins use FotMob team id. Display names use the most frequent spelling
for each id. The known multi-spelling ids are:

| id | observed spellings |
|---:|---|
| 4667 | Fuglafjoerdur / Fuglafjørdur |
| 8002 | B36 Torshavn / B36 Tórshavn |
| 8110 | NSI Runavik / NSÍ Runavík |
| 4666 | Vikingur / Víkingur |
| 4176 | TB Tvoeroyri / TB Tvøroyri |
| 2228 | Skála / Skala |
| 196125 | FC Suduroy / FC Suðuroy |

There are 13 distinct ids across the six seasons. Club churn is typically
two clubs per season. No feeder tier is present: 1. deild is absent from the
warehouse, and the Løgmanssteypið data is a cup final rather than a mover
prior source.

## Awarded-match quirk

Match 3822183 (2022-09-04, B36 Torshavn–B68 Toftir) has official score 0–3
and status reason `AW`, while its played event feed contains a 3–1 sequence
with four goal events. It is retained in the CSV for audit, with `awarded=1`
and `excluded=1`, but excluded from the 809-match fitting corpus. Every other
match has event-goal count equal to its official score.
