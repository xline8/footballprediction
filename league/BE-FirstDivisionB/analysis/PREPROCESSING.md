# Phase A — Preprocessing

build_data.py includes finished matches only, takes FT goals from header.status.scoreStr, orders rows by date and match ID, and keys all team logic on FotMob IDs.

Phase is mapped from general.leagueName: promotion/relegation group and promotion playoff receive explicit flags; plain “Belgian Challenger Pro League” maps to regular. All phases remain ordinary rows.

HT goals use FirstHalf stats only if a goals split is actually present; this feed has no such goals key, so the builder uses goal events at minute <=45 and labels ht_source=events; absent events remain none. No HT values are fabricated.

Stats are flattened from content.stats.Periods for All, FirstHalf and SecondHalf. Shotmap sums exclude penalty-shootout attempts. yellow_* and red_* use the stats feed when present, otherwise event fallback; event plain Yellow, Red and YellowRed counts remain separate. Missing feed is null, not zero. Referee is copied without imputation.

Outputs are gitignored regenerable artifacts: beb_matches.csv (1,114 rows) and beb_team_matches.csv (2,228 rows).

