# Step 2 — Preprocessing: BG-SecondLeague

- Builder: `data/build_data.py` (committed); output `data/bg2_matches.csv`
  (gitignored) + `bg2_team_matches.csv`, one row per **finished** match.
- Inclusion: index rows with league_id 9096 whose payload status is
  finished — 1,722 of 1,735. The 13 excluded rows are all in 2021/2022
  and are unplayed in their payloads, not a parsing loss.
- Score: `header.status.scoreStr`. Team ids/names: `general.homeTeam/awayTeam`.
- No stat columns exist to include — the CSV carries goals plus coverage
  flags (`has_stats`, `has_shotmap`, `has_events`, `referee`) so the
  absence is auditable from the CSV itself (all-zero / empty).
- Nothing is fabricated: no period splits, no xG, no referee are imputed.
- Season labels exactly as in the warehouse ("2021/2022", …).
- Count assert is a floor (>= 1700) so daily rebuilds with new finished
  matches pass, per the program's runner norm.
