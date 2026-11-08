# Step 2 — Preprocessing: SG-PremierLeague

Script: `data/build_data.py` (adapted from the BY-PremierLeague
scores-only build). Input: bundle `index_461.csv` (555 rows,
league_id 461) + the extracted JSON warehouse. Output:
`data/sg_matches.csv` (555 rows) + `data/sg_team_matches.csv`
(1,110 rows).

## Derivation rules (program standard, none negotiable)

- FT score from `header.status.scoreStr`; verified 0 mismatches
  against the index `score` column.
- Rows: only `status.finished` matches are kept — all 555 index
  rows are finished, so CSV count == index count (asserted in the
  script). No rows dropped.
- Phase from `general.leagueName`: "Premier League" → `main` and
  "S.League" → `main` (the same single-group competition before
  and after its rename). Unknown names would map to `unknown`
  (none occur).
- Team stats from `content.stats.Periods` (All / FirstHalf /
  SecondHalf) — the feed is absent, so all 19 stat keys × 3
  periods stay empty (NaN + `has_stats_all=0`, `has_stats_half=0`
  on every row). Missing stays missing; an absent feed is never
  read as zero.
- 1H goals / 1H yellows counted from event times (time ≤ 45, incl.
  45+ stoppage). Matches without events get `ht_source="none"` and
  null 1H fields — all 12 such matches are 0-0, so no dev goal is
  lost from the halves computation.
- Cards: BOTH sources recorded — stats yellows/reds (always null
  here) and event-derived counts (`ev_yellow_*` = Card events with
  card in {Yellow, YellowRed}; `ev_yellowred_*`, `ev_red_*`). The
  modelling target `yellow_*` is the event-derived unified
  yellows, recorded for EDA completeness; the K candidate is
  not-buildable (see EDA F5), so no cards target is ever fitted.
  Note: plain Yellow events are 0 in every season — `ev_yellow_*`
  counts YellowRed only in this league.
- Shotmap aggregates over regulation shots only — the shotmap is
  absent, so `has_shotmap=0` and all `sm_*` are 0/null on every
  row.
- Referee recorded as published (`referee`, `has_referee`) — null
  on every dev and virgin row (0% coverage in the dev era).
- `awarded` flag from `header.status.awarded` (0 matches);
  `score_events_mismatch` flags event goals ≠ header score
  (0 matches).
- Team table: one row per team-match (home + away), with goals
  for / against and the (empty) stat columns mirrored.

## Spot checks (3 raw JSONs, by hand)

- 3545559 (2021, Albirex Niigata FC–Hougang United FC): JSON
  `scoreStr` "3 - 1", leagueName "S.League", round 1, event goals
  3-1, HT goals 2-1, stats Periods empty, shotmap 0 — matches
  index and CSV.
- 4115183 (2024/2025): JSON "4 - 2", event goals 4-2, HT goals
  1-1 — matches index and CSV.
- 4890085 (2025/2026, virgin): JSON "1 - 0", event goals 1-0, HT
  goals 0-0 — matches index and CSV.
