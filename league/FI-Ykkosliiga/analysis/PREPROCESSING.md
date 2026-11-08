# Step 2 — Preprocessing: FI-Ykkosliiga

`data/build_data.py` regenerates `data/yk_matches.csv` (895 rows) and
`data/yk_team_matches.csv` (1,790 rows); both are ignored CSV artifacts.

All finished league_id 251 rows survive, with warehouse season labels unchanged.
FT goals come from `header.status.scoreStr`. `general.leagueName` maps regular
Ykkonen/Ykkönen/Ykkosliiga/Ykkösliiga and Championship, Relegation, and
Promotion Playoff suffixes to a phase flag; no phase is filtered.

HT goals use a `Half` event at time 45 (`ht_source=half_event`). If absent, goals
with event time ≤45 are counted (`ht_source=events`); if no event source exists,
HT fields are null. Cards are retained as event-derived yellow/red counts and
total Card events. Stats flags, shotmap counts, per-side shot/SOT/xG aggregates,
and xG presence are retained and asserted empty/zero. Referee text is copied
when named.

Rows are ordered `(date, match_id)` and team logic keys on FotMob team id. The
only usable target is goals. A later model run would warm on 2021, score
2022–2025 (n=598), and keep 2026 (complete, n=135) virgin; this brief performs
no fitting or virgin read.
