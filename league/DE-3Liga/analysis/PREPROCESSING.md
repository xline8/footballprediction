# Phase 2 — Preprocessing: DE-3Liga

Builder: `league/DE-3Liga/data/build_data.py` (port of the
DE-2Bundesliga builder, league_id 208). Source: the FotMob world
warehouse index (`data_enrichment/fotmob_world_index.csv`, paths
under `Germany/3. Liga/<season>/<id>.json`). No re-pull.

- Inclusion: played matches only — all 1,992 index rows for id 208
  carry a final score; output = 1,992 match rows + 3,984 team-match
  rows, reconciling one-to-one with the index (342 / 380 / 380 /
  380 / 380 / 130 by season).
- Season labels exactly as in the warehouse (`2021/2022` …
  `2026/2027`).
- Period splits: `fh_*`/`sh_*` stat columns are populated only where
  the source JSON carries period splits (0.6% of 2021/2022, 26.8% of
  2022/2023, ≥96.8% from 2023/2024) — never fabricated; halves
  constants are measured on the complete-splits era only
  (2023/2024–2025/2026).
- Phase: every row is `regular`; a `Qualification` league label
  would be flagged `qualification` and excluded — it never occurs
  in this corpus (verified in DATA_UNDERSTANDING §1), so all rows
  are ordinary rows in every fit and window.
- Cards target: event-unified yellows (`yellow_home/yellow_away`
  from events). The stats block undercounts (exact agreement only
  81.0% on stats-present rows, mean stats − events = −0.178/match;
  coordinator's independent all-rows check: exact 79.9%, mean
  +0.178 events over stats). Stats yellows are kept as
  `stats_yellow_*` for audit only.
- One stats-missing row (2021/2022) leaves SOT/corners/shots targets
  missing for that match — kept missing, never imputed; goals are
  complete in all 1,992 rows.
- Shotmap columns exist in the schema but are empty throughout
  (0/1,992 shotmaps): no xG anywhere in this league.
- CSVs are gitignored by repo norm; the builder is the committed,
  runnable artifact that regenerates them.
