# Preprocessing — IS-BestaDeildin

`data/build_data.py` filters league id 215 and finished payloads, reads the
full-time score, and records FotMob team ids and published names. It writes
`data/is_matches.csv` (942 rows) and `data/is_team_matches.csv` (1,884 rows).

All-period, first-half and second-half stat columns are retained without
imputation. Both stats-feed and event-feed yellows are retained: `yellow_*`
and `stats_yellow_*` are stats values, while `ev_yellow_*` counts Yellow and
YellowRed card events. The frozen K target is stats `yellow_cards` because
2025 event yellows are defective (27 zero-event matches versus 2 for stats).

Goals and event yellows use time <=45 for the first half. The referee is
`content.matchFacts.infoBox.Referee.text`. Empty shotmaps are represented by
structural zero `sm_*` columns and never treated as xG observations.

The 2023 box-touch series is quarantined. X7 windows may use box values from
2024 onward only; a failed min-8 window has multiplier 1.0 and is counted as
inactive. All logic keys on team id, including names with diacritic variants.
