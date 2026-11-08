# Preprocessing — IS-1Deild

The builder reads the shared index at `/home/hatch/workspace/footballprediction/data_enrichment/fotmob_world_index.csv` (the indexed payload paths resolve from that checkout), filters league id 216 and finished, non-cancelled matches, and writes `is1_matches.csv` (812 rows) plus `is1_team_matches.csv` (1,624 rows).

Full-time goals come only from `header.status.scoreStr`; this is the source of truth, including awarded match 3794991. First-half goals are counted from Goal events with `time <= 45`, credited by `isHome`. If the event list is empty, both HT fields are missing and `ht_source=none`; no imputation is performed.

The frozen phase rule is `playoff` when `general.leagueName` contains “Promotion Playoff” or `leagueRoundName` is `1/2` or `final`; otherwise it is `regular`. Playoffs remain in the fit/scoring scope planned for Phase B.

The event card field is deliberately named `ev_red_home/away`: it counts Red and YellowRed events together. There are no plain Yellow events in this corpus, so no yellow target is created. Stats, period splits, shotmaps/xG and referee names are absent in every payload. Structural `sm_*` zeros are retained only as coverage markers and are never treated as observations. Team identity is always keyed by FotMob team ID; display names are retained as published.

