# Preprocessing

`data/build_data.py` reads only the FNL index rows and their warehouse JSON
payloads. It writes one row per finished match to `fnl_matches.csv`, two
team-match rows to `fnl_team_matches.csv`, and the id/name audit to
`fnl_teams.csv`. These CSVs are generated artifacts and are gitignored.

The header score is the sole FT goals target. First-half goals are counted
from numeric Goal event times with minute ≤ 45. Event card counts are kept
separately as `ev_yellow_*`, `ev_yellowred_*`, and `ev_red_*`; no unified
Yellow target is fabricated where plain Yellow events do not exist.

The stats columns `ShotsOnTarget_*`, `corners_*`, `total_shots_*`,
`BallPossesion_*`, and `expected_goals_*` are deliberately present but
`None` in every row. Period split columns are not created as usable targets,
because no split block exists. Referee text is copied verbatim, including
empty or missing values. Shotmap, lineup, and player-stat presence flags are
stored for audit.

All matches have `phase=regular` and `included=1`. No phase filtering is
needed. Match ordering is by warehouse date and match id; model windows must
use strictly earlier kickoff times.
