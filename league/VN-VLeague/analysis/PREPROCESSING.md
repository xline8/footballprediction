# Phase 2 — Preprocessing

Builder: `league/VN-VLeague/data/build_data.py` (run from the repo root;
resolves the warehouse against the repo root, else the main checkout
`~/workspace/footballprediction`, read-only). Outputs (gitignored by repo
norm; the builder script is the committed artefact):

- `league/VN-VLeague/data/vn_vleague_matches.csv` — one row per finished
  match (969 rows).
- `league/VN-VLeague/data/vn_vleague_team_matches.csv` — one row per
  team-match (1,938 rows).

## Inclusion rules

- **Finished matches only** (`header.status.finished == true`). All 969
  index payloads are finished, so the rule drops nothing; it is kept so
  the CSV is reproducible if the warehouse ever gains unfinished rows.
- **One row per match id.** Match ids are globally unique across seasons
  (verified); the builder raises on a duplicate.
- **Official score is the target.** FT goals come from
  `header.status.scoreStr`. The one event-feed disagreement (match
  `4688919`, official 1–0 vs 2 event home goals) keeps the official
  score and is flagged `score_events_mismatch = True`.
- **Season labels as in the warehouse** (mixed: `2021`, `2022`, `2023`,
  `2023/2024`, `2024/2025`, `2025/2026`, `2026/2027`), plus
  `season_start` = first calendar year of the label, for ordering.
  Date ranges are disjoint and ids unique — no relabelling, no dedup
  beyond the id check.

## Split-source rules

- **HT goals** come from the Half-event marker (`halfStrShort='HT'`)
  where present (924 matches); `ht_source = 'half_event'`. Where the
  event feed is absent (45 matches), HT goals are null
  (`ht_source = 'none'`) — **never fabricated** from the FT score or
  from any league average. Cross-check: Half-event HT vs goal-event
  times ≤ 45 agrees 924/924.
- **Phase (2023 split group):** `phase = 'phase2_split_group'` for
  season `2023` matches dated ≥ 2023-07-15 (43 matches); everything
  else `phase = 'regular'`. FotMob's `matchRound` restarts at 1 in
  phase 2, so the round label alone is not used to separate phases.
- **Team identity:** FotMob team id. Canonical display name per id is
  the most frequent spelling in the corpus (11 ids have spelling
  variants; see DATA_UNDERSTANDING §3.3).
- **Stats / shotmap / xG columns** are emitted for all 20 known stat
  keys (home/away) and are null in every row — the schema is kept so
  the file is structurally comparable to sibling leagues, but the
  columns carry no data.
- **Cards:** event counts per kind (`ev_yellow_*`, `ev_red_*`,
  `ev_yellowred_*`) are recorded as observed, with the documented
  window (0 plain yellows before 2024/2025). Unified `yellow_*` /
  `red_*` columns are null and `cards_source = 'none'` — there is no
  stats feed to unify against, and the event feed is not a complete
  yellow record before 2024/2025.
- **Lineups / referee:** `has_lineup` is true only where a side has
  exactly 11 starters (413 matches, 2024/2025+); `referee` is null in
  every row (the infoBox text is empty in all 969 payloads).

## What is NOT in the CSV

- No imputed stats, no per-half stats (none exist), no xG, no SOT /
  corners / total shots, no referee identity, no player stats.
- No standings, h2h, or table snapshots (post-match; leakage risk).
- No 2026/2027 exclusion: the in-progress season is included in the
  CSV (49 rows, rounds 1–7) for inventory/levels, and excluded from
  fitting by the prereg windows.
