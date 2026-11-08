# Step 1 — Data Understanding: MA-BotolaPro (FotMob 530)

Source: FotMob world warehouse, `data_enrichment/fotmob_world_index.csv`
filtered to league_id 530; per-match payloads under
`fotmob_world/Morocco/Botola Pro/<season>/`. All counts below were
computed from the payload CONTENTS (full 1,255-file scan), not from
the index flags — the index `has_stats` flag is a key-presence flag
and is not trusted in this program (TH-ThaiLeague2 / ID-SuperLeague
precedents).

## Inventory

| season | n | dates | teams | rounds | stats (All) | events | matches w/ any yellow event | referee | period splits | shotmap |
|---|---|---|---|---|---|---|---|---|---|---|
| 2021/2022 | 240 | 2021-09-10 – 2022-07-05 | 16 | 30 | 0 | 209 | 21 | 0 | 0 | 0 |
| 2022/2023 | 240 | 2022-09-01 – 2023-06-23 | 16 | 30 | 0 | 214 | 36 | 0 | 0 | 0 |
| 2023/2024 | 240 | 2023-08-25 – 2024-06-14 | 16 | 30 | 0 | 215 | 34 | 0 | 0 | 0 |
| 2024/2025 | 240 | 2024-08-30 – 2025-05-12 | 16 | 30 | 172 | 238 | 187 | 0 | 0 | 0 |
| 2025/2026 | 240 | 2025-09-12 – 2026-07-05 | 16 | 30 | 226 | 240 | 236 | 0 | 0 | 0 |
| 2026/2027 | 55 | 2026-09-24 – 2026-11-08 | 16 | 7 (partial) | 49 | 55 | 55 | 0 | 0 | 0 |

Format (verified): 16 teams, straight double round-robin, exactly
30 rounds and 240 matches in every complete season, no play-off or
relegation-round rows in the feed. Every row is phase `regular`.
Seasons are split-year (Aug/Sep – May/Jun; 2021/2022 and 2025/2026
stretch into early July). 2025/2026 is the last COMPLETE season
(virgin). 2026/2027 is in progress (55 played) — reserved
confirmatory, never read by this build.

## The era map (the decisive fact of this league)

There is a hard feed break inside 2024/2025:

- **Before 2024-11-01** (all of 2021/2022–2023/2024 plus Aug–Oct
  2024): NO stats block at all. The events feed is a reduced feed —
  only `Goal`, `Half`, and `Card` events, and the `Card` events are
  exclusively `Red` (31/43/29 per season) and `YellowRed` (21/41/37):
  **zero plain `Yellow` events in three full seasons**. A yellows
  target therefore does not exist in this era. Substitutions are
  likewise absent.
- **Transition**: sporadic rich payloads appear 2024-10-22 –
  2024-10-26 (5 of 24 matches).
- **From 2024-11-01 onward**: every match is rich — stats block
  present (164/176 in Nov 2024–May 2025; 226/240 in 2025/2026),
  substitutions, and plain yellows at a plausible level (unified
  yellows mean 4.44/match in Nov–May 2024/2025; monthly mean jumps
  from 0.38–0.63 in Aug–Oct 2024 to 4.0–5.0 from November).

The rich era is therefore frozen as **matches dated >= 2024-11-01**.

## Stats feed content

Where present, the stats feed carries EXACTLY four keys, under
`Periods.All` only: `BallPossesion`, `total_shots`, `ShotsOnTarget`,
`corners`. There is no `FirstHalf`/`SecondHalf` period in ANY of the
1,255 payloads, no `expected_goals` or any xG key, no
`touches_opp_box`, no `big_chance`, no `yellow_cards` key, and no
shotmap (`content.shotmap` empty everywhere; index shotmap count 0
is confirmed true).

## Cards source decision input

The stats-vs-events artefact check is MOOT here: the stats feed has
no cards key at all, so no stats target exists to disagree with the
events. The only possible cards target is the event feed, and it is
valid only in the rich era (plain yellows exist only there). Target
frozen in PREPROCESSING / prereg: **event-unified yellows = Yellow +
YellowRed events** (RU-1Division convention), rich era only.

## Events cross-checks

- Goal events reconcile EXACTLY with the score in all 1,255 matches
  (goal-event count == score total, 2,120 dev-era goals). Event
  times are therefore a legitimate halves source for goals in every
  season, and for yellows in the rich era.
- Referee: `infoBox.Referee.text` is an empty string in all 1,255
  payloads. No referee feature can exist.
- Team identity: 25 distinct team ids across the corpus. Four ids
  carry two name spellings each (102033 'Difaa El Jadida'/'Difaâ El
  Jadida', 102043 'MAS Fès'/'MAS Fes', 316652 'RS Berkane'/'RSB
  Berkane', 102032 'CODM Meknès'/'CODM Meknes') — French/Arabic
  transliteration variants. All logic keys on team ids, never names.
