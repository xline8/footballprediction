# Phase 2 — Preprocessing: ES-LaLiga2

Builder: `league/ES-LaLiga2/data/build_data.py` (adapted from the
ENG-Championship builder / `league/jleague_lib.py` pattern).
Regenerate: `python3 league/ES-LaLiga2/data/build_data.py` from the
repo root (warehouse read from the main checkout, as in every
conveyor league). Outputs (gitignored): `data/es_matches.csv`
(2,478 rows) + `data/es_team_matches.csv` (4,956 rows).

## Rules

1. **Played matches only**: rows come from the warehouse index
   (league_id 140); a row is kept iff `header.status.finished`.
   All 2,478 index rows qualify; assert built == index count and
   match ids unique.
2. **FT score** from `header.status.scoreStr`; **HT score** from goal
   events with `time ≤ 45` (`ht_source='events'`; events present in
   every match).
3. **Phase flag**: `playoff` if matchRound ∈ {`1/2`, `final`} else
   `regular` (LaLiga2: rounds 1–42 regular, then the promotion
   play-offs). Play-off matches are ordinary rows in every fit; no
   phase feature is used anywhere. Every complete season holds its
   full 6 play-off matches — nothing is missing, nothing fabricated.
4. **Stats**: `content.stats.Periods` All/FirstHalf/SecondHalf,
   flattened for the fixed STAT_KEYS list. Period splits are taken
   only where present (0.2% in 2021/2022, 24.1% in 2022/2023, 100%
   from 2023/2024) — never fabricated; `has_stats_half` records it.
5. **Cards (unified target)**: event feed for every match
   (`cards_source='events'`): `yellow_*` counts matchFacts events
   with `type='Card'` and `card='Yellow'` by credited side;
   YellowRed/Red are reds, not yellows (the Phase 1 §3 decision,
   taken on dev-era evidence: the stats feed undercounts in every
   dev season and drops out entirely in 51 matches in 2021/2022).
   Stats-feed yellows kept alongside (`yellow_cards_*`) as the audit
   trail; event first-half yellows kept as `ev_yellow_1h_*` so the
   yellows halves constant uses the same event definition as the FT
   target; `ev_yellowred_*` / `ev_red_*` stored for the record.
   `red_*` = stats feed `red_cards` (reds are not a target).
6. **Shotmap aggregates**: regulation shots only (PenaltyShootout
   excluded); per side: shots, SOT (on-target and not blocked), ΣxG,
   ΣxGOT + count of shots carrying xGOT. (Era-dead for modelling —
   shotmap exists effectively only from 2025/2026 — but built for
   completeness, as in every conveyor league.)
7. **Referee**: `content.matchFacts.infoBox.Referee.text`, may be
   empty (51.5% of 2021/2022, 17.9% of the virgin).
8. **Season labels** exactly as in the warehouse
   (`2021/2022` … `2026/2027`).
9. **Team identity keyed on FotMob team id** (`home_team_id` /
   `away_team_id`, and `team_id` in the team-match table) everywhere.
   Names are display only: 10 of the 42 ids carry two spellings
   across seasons (accents dropped in some payloads). Any name-keyed
   membership test (movers, X2) uses accent-normalised names, which
   map 1:1 onto ids with no collisions (verified).
10. Team-match table: one row per team per match with for/against for
    goals, xG, shots, SOT, corners, yellows (stats + event), touches,
    big chances, possession + shotmap xG/shots.
