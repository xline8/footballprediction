# Stage A — Preprocessing

Run `python3 league/US-MLS/data/build_data.py`. It filters played index rows for league 130, asserts 3,054 matches / 6,108 team rows, sorts chronologically, and writes `us_matches.csv` and `us_team_matches.csv`.

Both regular and playoff matches are included and flagged. Calendar season labels remain strings (`2021`…`2026`); `season_start` is the integer year. 2026 is reserved/incomplete and excluded from modelling windows, EDA levels/reliability/halves, and gates.

FT score is `header.status.scoreStr`; HT goals come from credited goal events. Stats are the `All` period; first/second-half fields are populated only when supplied. Shotmap aggregates use regulation shots only: `PenaltyShootout` shots are excluded, while `n_shootout_shots` records them. Team identity is by FotMob id.

Phase uses `general.leagueName`, not `matchRound`: `Major League Soccer` → `regular`, `Major League Soccer Playoff` → `playoff`; raw league name is retained as `fotmob_league_name`.

Unified cards use the stats feed (`cards_source=stats`) and event yellow/red counts remain cross-check columns. Stats-feed yellow/red coverage is 99.15% in 2021, 99.39% in 2022, and 100% in 2023–25. The builder does not substitute event counts: missing stats cells remain missing rather than becoming zero or an event fallback. Referee is `matchFacts.infoBox.Referee.text`; empty is missing. No absent feed is imputed.
