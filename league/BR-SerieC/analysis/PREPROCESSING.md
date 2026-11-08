# Preprocessing — Brazil Série C

The build includes only finished payloads with a score. The 57 unfinished
2021 index rows are excluded; their index score is the placeholder `0-0` and
is not treated as a match result. The resulting `brc_matches.csv` has 1,229
finished matches and `brc_team_matches.csv` has 2,458 team-match rows.

The fit/evaluation rule is first phase plus second-stage / Promotion Round
groups. Final matches remain in the match CSV with `in_fit_set=0`: 12 final
legs in total are excluded from model fitting and gates.

Goals are taken from the finished score. Half-time goals are populated only
from Goal events when the Goal-event count equals the full-time score; when
that condition is false, `ht_home_goals`, `ht_away_goals`, and the split are
NULL and `ht_known=0`. The 2022 Mirassol–ABC match (4034464, 2–0) is the
known exception with zero Goal events, so it has no half split. No missing
score, statistic, referee, event-derived split, or target is imputed.

Team identity is the FotMob team ID. Display-name changes are retained as
labels only and never define joins or features. The frozen first-half goal
share, 0.443, is presentation-only.
