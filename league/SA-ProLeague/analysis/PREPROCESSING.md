# Phase 2 — Preprocessing: SA-ProLeague

Builder: `league/SA-ProLeague/data/build_data.py` (adapted from the
SCO builder / `league/jleague_lib.py` pattern). Regenerate:
`python3 league/SA-ProLeague/data/build_data.py` from the repo root
(warehouse read from the main checkout, as in every conveyor league).
Outputs (gitignored): `data/sa_matches.csv` (1,502 rows) +
`data/sa_team_matches.csv` (3,004 rows).

## Rules

1. **Played matches only**: rows come from the warehouse index
   (league_id 536); a row is kept iff `header.status.finished`.
   All 1,502 index rows qualify; match ids unique.
2. **FT score** from `header.status.scoreStr`; **HT score** from
   goal events with `time ≤ 45` (`ht_source='events'`).
3. **Phase**: `regular` for every row — the league has no split or
   playoff phase in any season (DATA_UNDERSTANDING §1).
4. **Stats**: `content.stats.Periods` All/FirstHalf/SecondHalf,
   flattened for the fixed STAT_KEYS list. Period splits are taken
   only where present (0% in 2021/2022, 35.8% in 2022/2023, 100%
   from 2023/2024) — never fabricated; `has_stats_half` records it.
5. **Cards (unified target)**: event feed — `yellow_*` =
   event Yellow + YellowRed counts, `cards_source='events'` for
   every match (events in 100%). Decided on dev-era evidence
   before any fitting (DATA_UNDERSTANDING §3.1): the stats feed
   undercounts in every dev-era season. Stats-feed counts stay as
   `yellow_cards_*` cross-check columns; reds (`red_*`) are
   stats-feed and are not a modelling target. First-half event
   yellows are stored (`fh_ev_yellow_*`, card events with
   `time ≤ 45`) for the halves constant.
6. **Shotmap aggregates**: regulation shots only (PenaltyShootout
   excluded); per side: shots, SOT (on-target and not blocked),
   ΣxG, ΣxGOT + count of shots carrying xGOT. Shotmap exists in
   100% of matches from 2023/2024, 2.5%/13.3% before — aggregates
   are 0/empty where the feed is absent and every consumer carries
   the era guard (FEATURES).
7. **Team identity**: names canonicalised by FotMob team id
   (id 101919 appears as "Al Qadsiah" and "Al Qadasiya"; the modal
   spelling wins). Engines key on the canonical name.
8. **Referee**: `content.matchFacts.infoBox.Referee.text`, may be
   empty (57.1% missing in 2021/2022, 99.3% in 2025/2026).
9. **Stadium**: name, city, latitude stored per match (climate
   check, DATA_UNDERSTANDING §4 — descriptive only, no feature).
10. **Season labels** exactly as in the warehouse
    (`2021/2022` … `2026/2027`).
11. Team-match table: one row per team per match with for/against
    for goals, xG, shots, SOT, corners, yellows, touches, big
    chances, possession + shotmap xG/shots.
