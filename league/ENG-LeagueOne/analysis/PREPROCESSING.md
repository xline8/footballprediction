# Phase 2 — Preprocessing: ENG-LeagueOne

Builder: `league/ENG-LeagueOne/data/build_data.py` (adapted from
the ENG-Championship builder / `league/jleague_lib.py` pattern).
Regenerate: `python3 league/ENG-LeagueOne/data/build_data.py` from
the repo root (warehouse read from the main checkout, as in every
conveyor league). Outputs (gitignored): `data/engl1_matches.csv`
(2,943 rows) + `data/engl1_team_matches.csv` (5,886 rows).

## Rules

1. **Played matches only**: rows come from the warehouse index
   (league_id 108); a row is kept iff `header.status.finished`.
   All 2,943 index rows qualify; assert built >= 2,943 (floor form
   for daily rebuilds) and match ids unique.
2. **FT score** from `header.status.scoreStr`; **HT score** from goal
   events with `time ≤ 45` (`ht_source='events'`).
3. **Phase flag**: `playoff` if matchRound ∈ {`1/2`, `final`} else
   `regular` (League One: rounds 1–46 regular, then the promotion
   play-offs — 5 per season, all present in the warehouse copy,
   finals included). Play-off matches are ordinary rows in every
   fit; no phase feature is used anywhere.
4. **Stats**: `content.stats.Periods` All/FirstHalf/SecondHalf,
   flattened for the fixed STAT_KEYS list. Period splits are taken
   only where present (0.4% in 2021/2022, 21.2% in 2022/2023, ~100%
   from 2023/2024) — never fabricated; `has_stats_half` records it.
5. **Cards (unified target)**: stats feed `yellow_cards`/`red_cards`
   (`cards_source='stats'` for every match — agreement with the
   event feed is 89.0% exact with no systematic undercount, unlike
   the AR/BR/NO artefact); event-feed Yellow counts kept alongside
   (`ev_yellow_*`) as the audit trail.
6. **Shotmap aggregates**: regulation shots only (PenaltyShootout
   excluded); per side: shots, SOT (on-target and not blocked), ΣxG,
   ΣxGOT + count of shots carrying xGOT. Shotmap exists in only
   3.2% of 2021/2022 matches — aggregates are 0/empty there by
   absence, and every consumer must era-guard (FEATURES).
7. **Referee**: `content.matchFacts.infoBox.Referee.text`, may be
   empty (50.4% of 2021/2022).
8. **Season labels** exactly as in the warehouse
   (`2021/2022` … `2026/2027`).
9. Team-match table: one row per team per match with for/against for
   goals, xG, shots, SOT, corners, yellows, touches, big chances,
   possession + shotmap xG/shots.
