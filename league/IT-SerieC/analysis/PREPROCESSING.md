# Step 2 — Preprocessing: IT-SerieC

- Builder: `data/build_data.py`; outputs `data/itseriec_matches.csv` and
  `data/itseriec_team_matches.csv`, one row per finished match.
- Inclusion: all 6,184 index rows are finished at this pull. No row was lost
  to parsing. The modeling set is the 5,936 rows with `phase == regular`;
  248 Super Cup/playoff/playout rows are retained in the CSV but excluded from
  modeling.
- Score: `header.status.scoreStr`. Team identity is carried by FotMob ids and
  names. Group is derived only from `general.leagueName == Serie C Grp. X`.
- Coverage flags (`has_stats`, `has_shotmap`, `has_events`, `referee`) preserve
  auditable payload coverage. Nothing is fabricated: no xG, period split,
  referee, or market target is imputed.
- Season labels are unchanged from the warehouse.
