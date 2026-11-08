# Step 2 — Preprocessing: IT-SerieB

Builder: `league/IT-SerieB/data/build_data.py` (adapted from the
ES-LaLiga2 builder). Regenerate: `python3
league/IT-SerieB/data/build_data.py` from the repo root (warehouse
read from the main checkout, as in every conveyor league).
Outputs (gitignored): `data/itserieb_matches.csv` (2,059 rows) +
`data/itserieb_team_matches.csv` (4,118 rows).

## Rules

1. **Played matches only**: rows come from the warehouse index
   (league_id 86); a row is kept iff `header.status.finished`.
   All 2,059 index rows qualify; match ids unique (asserted).
2. **FT score** from `header.status.scoreStr`; **HT score** from
   goal events with `time ≤ 45` (events present in every match).
3. **Phase flag** from `general.leagueName`: `Serie B` → `regular`;
   `Serie B Promotion Playoff` → `promotion_playoff`;
   `Serie B Relegation Playoff` → `relegation_playoff`. Play-off /
   play-out matches are ordinary rows in every fit; no phase
   feature is used anywhere (DATA_UNDERSTANDING phase rule).
4. **Stats**: `content.stats.Periods` All/FirstHalf/SecondHalf,
   flattened for the fixed STAT_KEYS list. Period splits taken
   only where present (1.0% in 2021/2022, 28.7% in 2022/2023,
   ~100% from 2023/2024) — never fabricated; `has_stats_half`
   records it.
5. **Cards (unified target)**: event feed for every match
   (`cards_source='events'`): `yellow_*` counts matchFacts events
   with `type='Card'` and `card='Yellow'` by credited side;
   YellowRed/Red are reds, not yellows (Phase 1 decision, taken on
   dev-era evidence: the stats feed undercounts in every dev
   season, −1.6% to −3.9%). Stats-feed yellows kept alongside
   (`yellow_cards_*`) as the audit trail; event first-half yellows
   kept as `ev_yellow_1h_*` so the yellows halves constant uses
   the same event definition as the FT target. `red_*` = stats
   feed `red_cards` (reds are not a target).
6. **Shotmap aggregates**: regulation shots only (PenaltyShootout
   excluded); per side: shots, SOT, ΣxG, ΣxGOT + count. (Era-dead
   for modelling — shotmap exists effectively only from
   2025/2026 — but built for completeness.)
7. **Referee**: `content.matchFacts.infoBox.Referee.text`, may be
   empty (52.6% of 2021/2022, 24.6% of the virgin).
8. **Season labels** exactly as in the warehouse
   (`2021/2022` … `2026/2027`).
9. **Team identity keyed on FotMob team id** everywhere, with one
   documented alias: Reggiana id 959006 (Aug–Nov 2023) →
   canonical 6500 (the two ids never co-occur; complementary
   15 + 23 = 38 matches in 2023/2024). After the alias every
   season holds exactly 20 ids (46 distinct overall). Names are
   display only; the one name-keyed test (X2 mover membership)
   uses accent-normalised names plus the spelling alias
   `ac reggiana 1919` → `reggiana`.
10. Team-match table: one row per team per match with for/against
    for goals, xG, shots, SOT, corners, yellows (stats + event),
    touches, big chances, possession + shotmap xG/shots.
