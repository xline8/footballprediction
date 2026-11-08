# Preprocessing

`data/build_data.py` adapts the UY-LigaAUF scores-only parser. It reads the filtered index, resolves warehouse-relative JSON paths, uses header scores/status, preserves event counts, derives first-half goals from event minutes `<=45`, and canonicalises names by FotMob team ID. Stats and split columns remain missing with `has_stats_all=False` and `has_stats_half=False`; unified card targets remain missing because the event feed has no consistent yellow-card series.

Inclusion is finished payloads only. The generated [uy_segunda_matches.csv](../data/uy_segunda_matches.csv) has 1,166 rows: 85 + 169 + 231 + 233 + 230 + 218. The team-match file has 2,332 rows. Goals sum to 2,601, season totals are 179, 365, 557, 495, 498, and 507. Event goals agree with scores wherever events are present; empty-event matches retain score-derived goals and missing event-derived fields.
