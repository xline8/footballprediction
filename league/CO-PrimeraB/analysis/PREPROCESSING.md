# Step 2 — Preprocessing: CO-PrimeraB

- Builder: `league/CO-PrimeraB/data/build_data.py` (committed);
  regenerates `co_primerab_matches.csv` (gitignored) from the FotMob
  world index (league_id 9125) + per-match JSONs in the main checkout.
- Inclusion: **finished matches only** (`header.status.finished`).
  This excludes the 134 unfinished 0-0 placeholder files of season
  2021 (see DATA_UNDERSTANDING) — the single most important rule in
  this league. Output: 1,639 rows (2021: 144, 2022: 289, 2023: 310,
  2024: 310, 2025: 308, 2026: 278).
- Columns: match_id, season (warehouse label, calendar year), date,
  round, tournament, phase (regular / quadrangular / final, derived
  from tournament name and round string per the frozen rule in
  DATA_UNDERSTANDING), home/away team id + name, home_goals,
  away_goals, goals_1h + events_exact (goal events ≤ 45' counted only
  where the event feed exactly reproduces the score; blank otherwise
  — never fabricated), home_red/away_red (header counts, retained
  for the record; NOT a cards target), home_mover_down /
  away_mover_down (team absent from Primera B in season S−1 and
  present in Primera A, league_id 274, in calendar year S−1; team_id
  based; all false for 2021).
- No period-split source exists, so nothing is fabricated: halves
  are handled only via the frozen constant in FEATURES.
- Team identity = FotMob team_id everywhere downstream (names vary
  by season: accents and rebrands).
- Sort order: date, then match_id.
