# Step 2 — Preprocessing (RO-LigaII)

Builder: `league/RO-LigaII/data/build_data.py`, regenerating `rl2_matches.csv` and `rl2_team_matches.csv`. The builder asserts 1,513 rows and unique match ids. The match CSV is one row per finished index row; the team CSV is two rows per match with goals for/against only.

## Inclusion rules

1. Keep finished matches only and take FT goals from `header.status.scoreStr`.
2. Map `Tournament.leagueName` exactly: `Liga II` → `regular`, `Promotion Group` → `promotion`, `Relegation Group A/B` → `relegation_a` / `relegation_b`, and `Relegation Playoff` → `relegation_playoff`.
3. Keep playoff rows in the CSV for audit, but modelling inclusion is `phase != relegation_playoff`: 262, 262, 262, 262, 317 and 140 by season, 1,505 total.
4. Preserve warehouse season labels exactly (`2021/2022` through `2026/2027`). No 2026/2027 rows are read for modelling in this build.

## Column rules

The schema is intentionally minimal: match id, league, season, date, round, sub-league id, phase, team ids/names, FT goals, event-derived HT goals, `ht_source`, event red/YellowRed counts, explicit zero straight-yellow counts, `has_events`, `referee`, explicit `has_stats=0`, `has_shotmap=0`, `n_shotmap_shots=0`, and coverage level. No stats columns are invented.

HT goals count goal events with `time <= 45`. They are populated only when the event list is non-empty; otherwise both values are null and `ht_source=none`, including the 0–3 feed-gap match. Referee is null throughout. Straight yellows are explicitly zero because no straight-Yellow event occurs in the corpus. `ev_red_*` and `ev_yellowred_*` remain audit counts only.
