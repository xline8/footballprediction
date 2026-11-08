# Phase 2 — Preprocessing

`build_data.py` reads every league-8935 index row and asserts stats-null,
shotmap-empty, parent league 8935, and lower coverage. It parses FT goals,
maps phases, preserves FotMob team IDs, and writes one match row plus two
team rows per match.

Goal event times <=45 define the first-half split. `ht_validated` is exact
for event/FT agreement, and also for a no-event 0–0 whose split is
trivially 0–0; walkovers and the one mismatch remain unvalidated.
`ht_source` records `events` or `none`. No target is invented for the
missing stats markets. CSVs are ignored by repository policy.
