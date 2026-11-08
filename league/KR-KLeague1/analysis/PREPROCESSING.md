# Phase 2 — Preprocessing: KR-KLeague1

`data/build_data.py` writes gitignored `kr_matches.csv` and
`kr_team_matches.csv` from finished league 9080 index rows. It preserves
season labels and labels rounds >=34 `split`; no split match is excluded.

FT goals use `scoreStr`; HT goals use event goals with `time <= 45`. Stats
are copied without imputation (`All`, `fh_`, and `sh_` prefixes). Shotmaps
exclude penalty shootouts and retain shots, SOT, xG, xGOT sums/counts, and
first-half shots. The long table has two team-ID rows per match.

Both yellow sources are retained: `yellow_cards_*` (stats) and `ev_yellow_*`
(events). DEV agreement: 683 matches had both sources, 630 agreed and 53
disagreed; means were 3.341 stats versus 3.404 events, events were larger in
47 disagreements and stats in 6, with mean stats-minus-events difference
-0.811. Stats are absent in 2021 while events are complete. The unified
`yellow_*` target therefore uses events whenever events exist, with stats
fallback only when events are absent; `cards_source` records this.

No standings, attendance, lineup, or post-match snapshot is used.
