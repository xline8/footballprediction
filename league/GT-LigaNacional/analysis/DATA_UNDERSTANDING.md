# Data understanding — Guatemala Liga Nacional

Frozen measurement date: 2026-11-10. The FotMob world warehouse was filtered
to `league_id=336`. The index contains 1,443 rows and every corresponding
payload has `header.status.finished=true`; no rows were excluded.

## Content inventory

| season | n | stats | shotmap shots >0 | xG shots | period splits | referee named | card-event matches | HT recoverable | events present |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2021/2022 | 292 | 0 | 0 | 0 | 0 | 0 | 62 | 263 | 263 |
| 2022/2023 | 292 | 0 | 0 | 0 | 0 | 0 | 89 | 272 | 272 |
| 2023/2024 | 220 | 0 | 0 | 0 | 0 | 0 | 80 | 203 | 203 |
| 2024/2025 | 234 | 0 | 0 | 0 | 0 | 0 | 83 | 208 | 208 |
| 2025/2026 | 292 | 0 | 0 | 0 | 0 | 0 | 102 | 276 | 276 |
| 2026/2027 | 113 | 0 | 0 | 0 | 0 | 0 | 43 | 110 | 110 |

Card-event matches are not card counts. The payload contains 570 `Card`
events in total: 44/31 Red/YellowRed in 2021/22, 70/38 in 2022/23,
69/34 in 2023/24, 84/16 in 2024/25, 120/8 in 2025/26, and 55/1 in
2026/27. There are no `Card=Yellow` events. This is a dismissal feed, not a
stable yellow-card target.

The last kickoff dates are 2026-05-24 for 2025/26 and 2026-11-09 for
2026/27. Thus 2025/26 is complete in this pull and 2026/27 is in progress.
There are 1,332 matches with event payloads and 111 without. Of the
111 no-event matches, 110 are 0-0 draws and one (match 4487139,
2024/2025, 0-3) has no events at all, so a missing event feed must not
be read as a 0-0 inference rule. Header scores are the full-time
source; a sample-wide cross-check found seven event/header score
mismatches, all of them header 3-0 or 0-3 results whose recorded goal
events sum to fewer goals (match ids 3787936, 3787969, 4088236,
4088340, 4394817, 4819882, 5861246) — the awarded-score pattern. The
event-derived half-time values of those seven matches are likewise
inconsistent with the header score and are descriptive only.

## Format and identity

FotMob team ID is the identity key; display names are retained for reading.
Each historical season is a split Apertura/Clausura competition with separate
final stages. Payload phase totals are:

| season | phase totals |
|---|---|
| 2021/2022 | Apertura 132; Clausura 132; Apertura Final Stage 14; Clausura Final Stage 14 |
| 2022/2023 | Apertura 132; Clausura 132; Apertura Final Stage 14; Clausura Final Stage 14 |
| 2023/2024 | Apertura 96; Clausura 96; Apertura Final Stage 14; Clausura Final Stage 14 |
| 2024/2025 | Apertura 96; Clausura 110; Apertura Final Stage 14; Clausura Final Stage 14 |
| 2025/2026 | Apertura 133; Clausura 146; Apertura Final Stage 13 |
| 2026/2027 | Apertura 113; season in progress at the frozen pull |

The 220 and 234 totals are therefore format/phase totals, not excluded
finished rows: 2023/24 has 16-round regular phases (96 each), while 2024/25
has a 16-round Apertura and 22-round Clausura. The 2024/25 Clausura has
only 11 distinct teams (5 matches per round) against 12 in the Apertura —
one club is absent from that half-season — which accounts for 110 rather
than 132 Clausura matches. 2025/26 also has a changed
phase allocation and one final-stage count short of the earlier pattern.

Half-time goals are recovered only from goal events. No period splits exist;
missing half-time values remain missing and no half constant is frozen.
There is no other Guatemala league in the warehouse, so no X2 cross-tier
mover evidence exists.

## Gaps and quirks

`content.stats` is `None` in all 1,443 finished payloads. Shotmaps are present
only as empty shells, with zero shots and zero xG shots. There are no named
referees, lineups, or period-split stats. The complete machine-readable
measurements are in `eda_summary.json` and `inventory_summary.json`.
