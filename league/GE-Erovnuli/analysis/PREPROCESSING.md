# Step 2 — Preprocessing: GE-Erovnuli

- Builder: `league/GE-Erovnuli/data/build_data.py` (committed);
  regenerates `ge_matches.csv` (gitignored) from the FotMob world
  index (league_id 439) + per-match JSONs in the main checkout.
- Inclusion: played matches only — all 1,059 indexed rows are finished
  with a score; no exclusions were needed.
- Columns: match_id, season (warehouse label, calendar year), date,
  round, home/away team id + name, home_goals, away_goals, goals_1h
  (goal events with time ≤ 45 — event-derived, exact per the Step-1
  audit), home_red/away_red (header counts, retained for the record;
  NOT a cards target — see DATA_UNDERSTANDING).
- No period-split source exists, so nothing is fabricated: halves are
  handled only via the frozen constant in FEATURES.
- Team identity = FotMob team_id everywhere downstream.
- Sort order: date, then match_id. Output verified: 1,059 rows,
  season counts 180×5 + 159.
