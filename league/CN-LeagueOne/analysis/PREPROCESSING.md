# Step 2 — Preprocessing: CN-LeagueOne

Script: `data/build_data.py` (adapted from the NO-2Divisjon build,
itself the FI reference build + the IL scores-only precedent).
Input: bundle `index_9137.csv` (1,572 rows, league_id 9137) + the
extracted JSON warehouse. Output: `data/cn_matches.csv` (1,572
rows) + `data/cn_team_matches.csv` (3,144 rows).

Note on the bundle layout: the release tarball
`bundle-cn-league1` / `cn1_slice.tar.gz` carries its JSONs under
`China/China League One/<season>/` (no
`data_enrichment/fotmob_world/` prefix); the files were moved into
the warehouse layout above at extraction time, so every index
`path` resolves. No JSON content was altered.

## Derivation rules (program standard, none negotiable)

- FT score from `header.status.scoreStr`; verified 0 mismatches
  against the index `score` column.
- Rows: only `status.finished` matches are kept — all 1,572 index
  rows are finished, so CSV count == index count (asserted in the
  script). No rows dropped.
- Phase from `general.leagueName`: "China League" → `single`.
  Unknown names would map to `unknown` (none occur).
- Team stats from `content.stats.Periods` (All / FirstHalf /
  SecondHalf) — the feed is absent, so all 19 stat keys × 3 periods
  stay empty (NaN + `has_stats_all=0`, `has_stats_half=0` on every
  row). Missing stays missing; an absent feed is never read as zero.
- 1H goals / 1H yellows counted from event times (time ≤ 45, incl.
  45+ stoppage). Matches without events get `ht_source="none"` and
  null 1H fields.
- Cards: BOTH sources recorded — stats yellows/reds (always null
  here) and event-derived counts (`ev_yellow_*` = Card events with
  card in {Yellow, YellowRed}; `ev_yellowred_*`, `ev_red_*`). The
  modelling target `yellow_*` is the event-derived unified yellows,
  recorded for EDA completeness; the K candidate is not-buildable
  (see EDA F5), so no cards target is ever fitted.
- Shotmap aggregates over regulation shots only — the shotmap is
  absent, so `has_shotmap=0` and all `sm_*` are 0/null on every row.
- Referee recorded as published (`referee`, `has_referee`) — null on
  every row (0% coverage).
- `awarded` flag from `header.status.awarded`; `score_events_mismatch`
  flags matches where event goals ≠ header score (0 occur).
- Team table: one row per team-match (home + away), with goals for /
  against and the (empty) stat columns mirrored.

## Spot checks (3 raw JSONs, by hand)

- 3574318 (2021, Wuhan Three Towns–Beijing Technology): JSON
  `scoreStr` "3 - 1", leagueName "China League", round 1 — matches
  index and CSV.
- 3574267 (2021, Zibo Cuju–Zhejiang Professional): JSON "0 - 4",
  6 events — matches index and CSV.
- 3892074 (2022, Kunshan FC–Beijing Technology): JSON "3 - 0",
  `awarded=true`, 0 events — matches index and CSV; header wins,
  awarded flag carried.
