# Phase 2 — Preprocessing: ENG-Championship

Builder: `league/ENG-Championship/data/build_data.py` (adapted from
the SCO builder / `league/jleague_lib.py` pattern). Regenerate:
`python3 league/ENG-Championship/data/build_data.py` from the repo
root (warehouse read from the main checkout, as in every conveyor
league). Outputs (gitignored): `data/engch_matches.csv` (2,963 rows)
+ `data/engch_team_matches.csv` (5,926 rows).

## Rules

1. **Played matches only**: rows come from the warehouse index
   (league_id 48); a row is kept iff `header.status.finished`.
   All 2,963 index rows qualify; assert built == index count and
   match ids unique.
2. **FT score** from `header.status.scoreStr`; **HT score** from goal
   events with `time ≤ 45` (`ht_source='events'`).
3. **Phase flag**: `playoff` if matchRound ∈ {`1/2`, `final`} else
   `regular` (Championship: rounds 1–46 regular, then the promotion
   play-offs). Play-off matches are ordinary rows in every fit; no
   phase feature is used anywhere. The 2025/2026 warehouse copy is
   missing one semi-final tie (2 matches) — recorded in
   DATA_UNDERSTANDING §1; nothing is fabricated to fill it.
4. **Stats**: `content.stats.Periods` All/FirstHalf/SecondHalf,
   flattened for the fixed STAT_KEYS list. Period splits are taken
   only where present (3.1% in 2021/2022, 19.6% in 2022/2023, ~100%
   from 2023/2024) — never fabricated; `has_stats_half` records it.
5. **Cards (unified target)**: stats feed `yellow_cards`/`red_cards`
   (`cards_source='stats'` for every match — agreement with the
   event feed is 91.3% exact with no systematic undercount, unlike
   the AR/BR/NO artefact); event-feed Yellow counts kept alongside
   (`ev_yellow_*`) as the audit trail.
6. **Shotmap aggregates**: regulation shots only (PenaltyShootout
   excluded); per side: shots, SOT (on-target and not blocked), ΣxG,
   ΣxGOT + count of shots carrying xGOT.
7. **Referee**: `content.matchFacts.infoBox.Referee.text`, may be
   empty (51.7% of 2021/2022).
8. **Season labels** exactly as in the warehouse
   (`2021/2022` … `2026/2027`).
9. Team-match table: one row per team per match with for/against for
   goals, xG, shots, SOT, corners, yellows, touches, big chances,
   possession + shotmap xG/shots.
