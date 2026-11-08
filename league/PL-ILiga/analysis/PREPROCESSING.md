# Phase 2 — Preprocessing: FotMob I Liga Analysis Tables

build_data.py reads league_id 197, sorts by date and match id, and writes 1,671 match rows and 3,342 team rows. All 1,671 rows are finished and retained.

## Inclusion and phase

Played rows are included, including the 3 playoff rows in every complete season. phase=regular for matchRound 1–34 and phase=playoff for 1/2 and final. Playoff rows remain in the CSV but are excluded from every fit and gate.

## Derivation rules

- FT goals use header.status.scoreStr, falling back to the index score.
- Team identity uses FotMob ids; names are labels only.
- HT goals use Goal events with time <= 45, excluding penalty-shootout events. ht_source=events only when an events block exists; otherwise HT goals are null and ht_source=none.
- Stats, xG, shots, corners, shotmap, and referee fields remain null because those feeds are absent.
- yellow_*, red_* are null and cards_source=none for every row. ev_red_* counts Red plus YellowRed events. ev_yellow_* is zero with provenance only; it is never a target input.
- When events and shotmap are absent, stat and shotmap fields are nulled rather than zero-filled.

Season labels are preserved exactly as stored in the warehouse: 2021/2022 through 2026/2027. The builder asserts the 1,671 rows, unique match ids, 306 regular plus 3 playoff rows in each complete season, and 126 rows in 2026/2027.

