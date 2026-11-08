# Step 2 — Preprocessing: Tanzania Premier League

`data/build_data.py` reads one row per Tanzania index row and the payload named by its `path`. It deterministically writes `tz_matches.csv` (1,284 rows) and `tz_team_matches.csv` (2,564 rows, eligible matches only).

Frozen rules:

1. Keep exactly one output row per index row. The index has 1,284 rows and no duplicate match IDs.
2. Eligibility is the payload `header.status.awarded` flag or `header.status.reason.short == "AW"`; this yields 1,282 eligible rows. The eventless 3–0/0–3 inference agrees except on played-then-awarded `4950929`.
3. Goals, date, and identity are read from the index and cross-checked against payload header/general. The header score agrees on 1,284/1,284; goal-event score agreement is separately audited, not substituted for the official score.
4. HT goals come only from a `Half` event at time 45. No HT values are fabricated or imputed. `4950929` is the sole `ht_suspect` row and is excluded because it is AW.
5. Season labels are copied as stored. Round comes from `content.matchFacts.infoBox.Tournament.round` with `general.matchRound` as the structural fallback.
6. Teams are keyed by displayed name, not merged across the two documented rename pairs. Team IDs are retained where present.
7. No stats, shotmap, player, referee, or lineup imputation is performed.

Match columns are: `match_id`, `league`, `season`, `date`, `round`, `sub_tournament`, `stage`, home/away team IDs and names, `finished`, `awarded`, home/away goals, `has_events`, `n_events`, `n_goal_events`, `n_card_events`, `n_red_events`, HT goals, `ht_source`, `ht_suspect`, `has_stats_all`, `has_stats_half`, `has_shotmap`, `referee`, `has_lineup`, `lineup_block`, and `eligible`.

Team-match columns are match ID, season, date, stage, sub-tournament, team ID/name, venue, goals for and goals against.
