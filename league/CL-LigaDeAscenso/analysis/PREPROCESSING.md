# Step 2 — Preprocessing — CL-LigaDeAscenso

Builder: `league/CL-LigaDeAscenso/data/build_data.py` (regenerates
`cla_matches.csv` + `cla_team_matches.csv` from the warehouse index;
CSVs are gitignored by repo norm). One row per index row (1,515),
sorted by (date, match_id).

Inclusion and labelling rules (all frozen here, before any fitting):

- **Played rule:** `finished` = payload `header.status.finished`.
  Only `finished = 1` rows are played matches. This removes the 62
  never-started 2021 placeholders with fake 0-0 scores
  (DATA_UNDERSTANDING). Unfinished rows stay in the CSV, flagged,
  for audit; nothing downstream reads them.
- **Phase rule:** `phase = playoff` when the payload league name is
  a "Promotion Playoff" instance (2021–2024) or the round name is a
  "Promotion Play-offs - …" round (2025); otherwise `regular`.
  Play-off ties are excluded from every fit and score in every
  candidate (frozen in the prereg).
- **Modelling population:** `finished = 1 AND phase = regular`:
  178 (2021) + 272 (2022) + 240 (2023) + 240 (2024) + 240 (2025) +
  233 (2026, incomplete) = 1,403 rows.
- **Scores:** from `header.status.scoreStr`, falling back to the
  index `score` (verified identical on samples; header teams' ids
  and names come from `header.teams`).
- **Season labels:** exactly as in the warehouse index (calendar
  years "2021"…"2026").
- **Team identity:** keyed on FotMob team id everywhere; display
  names canonicalised to the last-seen spelling per id (4
  multi-spelling ids, DATA_UNDERSTANDING).
- **Stats columns:** parsed from payload content with the parent
  league's parser; they are null on **every** row of this league
  (the stats block is an empty shell — DATA_UNDERSTANDING).
  `has_stats_all` / `has_stats_half` are computed from parsed
  **values**, never from the index flags, and are 0 on all 1,515
  rows.
- **Event-derived columns:** goal-event counts and HT goals
  (`time <= 45`, penalty-shootout events excluded, parent-league
  convention), `goals_events_complete` = (goal events == score
  total), and event card counts by type/side. Event yellows are
  retained for audit only — they are **not** a cards target (no
  plain yellows exist before 2025).
- **Splits:** no period splits exist in this league; nothing is
  fabricated. Halves presentation for goals uses goal-event times
  only (FEATURES).
