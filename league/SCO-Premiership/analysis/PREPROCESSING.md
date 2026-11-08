# Phase 2 — Preprocessing: SCO-Premiership

Builder: `league/SCO-Premiership/data/build_data.py` (adapted from the
DK builder / `league/jleague_lib.py` pattern). Regenerate:
`python3 league/SCO-Premiership/data/build_data.py` from the repo root
(warehouse read from the main checkout, as in every conveyor league).
Outputs (gitignored): `data/sco_matches.csv` (1,215 rows) +
`data/sco_team_matches.csv` (2,430 rows).

## Rules

1. **Played matches only**: rows come from the warehouse index
   (league_id 64); a row is kept iff `header.status.finished`.
   All 1,215 index rows qualify; assert built == index count and
   match ids unique.
2. **FT score** from `header.status.scoreStr`; **HT score** from goal
   events with `time ≤ 45` (`ht_source='events'`).
3. **Phase flag**: `split` if matchRound ≥ 34 else `regular`
   (Scotland: rounds 1–33 regular, 34–38 split). Split matches are
   ordinary rows in every fit; no phase feature is used anywhere.
4. **Stats**: `content.stats.Periods` All/FirstHalf/SecondHalf,
   flattened for the fixed STAT_KEYS list. Period splits are taken
   only where present (0% in 2021/2022, 30.7% in 2022/2023, 100%
   from 2023/2024) — never fabricated; `has_stats_half` records it.
5. **Cards (unified target)**: stats feed `yellow_cards`/`red_cards`
   (`cards_source='stats'` for every match); event-feed Yellow
   counts kept alongside (`ev_yellow_*`) as the audit trail.
6. **Shotmap aggregates**: regulation shots only (PenaltyShootout
   excluded); per side: shots, SOT (on-target and not blocked), ΣxG,
   ΣxGOT + count of shots carrying xGOT.
7. **Referee**: `content.matchFacts.infoBox.Referee.text`, may be
   null (52.6% of 2021/2022).
8. **Season labels** exactly as in the warehouse
   (`2021/2022` … `2026/2027`).
9. Team-match table: one row per team per match with for/against for
   goals, xG, shots, SOT, corners, yellows, touches, big chances,
   possession + shotmap xG/shots.
