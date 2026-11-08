# Step 2 — Preprocessing: BY-PremierLeague

Script: `data/build_data.py` (adapted from the FR-Ligue3
scores-only build). Input: bundle `index_263.csv` (1,394 rows,
league_id 263) + the extracted JSON warehouse. Output:
`data/by_matches.csv` (1,394 rows) + `data/by_team_matches.csv`
(2,788 rows).

## Derivation rules (program standard, none negotiable)

- FT score from `header.status.scoreStr`; verified 0 mismatches
  against the index `score` column.
- Rows: only `status.finished` matches are kept — all 1,394 index
  rows are finished, so CSV count == index count (asserted in the
  script). No rows dropped.
- Phase from `general.leagueName`: "Premier League" → `main`
  (single group every season). Unknown names would map to `unknown`
  (none occur).
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
  (see EDA F5), so no cards target is ever fitted. Note: plain
  Yellow events are 0 in every season — `ev_yellow_*` counts
  YellowRed only in this league.
- Shotmap aggregates over regulation shots only — the shotmap is
  absent, so `has_shotmap=0` and all `sm_*` are 0/null on every row.
- Referee recorded as published (`referee`, `has_referee`) — null on
  every row (0% coverage).
- `awarded` flag from `header.status.awarded`; `score_events_mismatch`
  flags the 2 matches where event goals ≠ header score (4127429
  awarded 3-0 vs played 2-2; 3832371 header 0-0 vs 5 event goals
  4-1 — official result 0-0; header wins in both).
- Team table: one row per team-match (home + away), with goals for /
  against and the (empty) stat columns mirrored.

## Spot checks (3 raw JSONs, by hand)

- 3540809 (2021, Isloch–Slavia Mozyr): JSON `scoreStr` "1 - 0",
  leagueName "Premier League", round 1, 1 event goal, stats Periods
  empty, shotmap 0 — matches index and CSV.
- 3540973 (2021, Dynamo Brest–Sputnik Rechitsa): JSON "3 - 0",
  awarded; no event feed at all (withdrawn club's fixture) —
  header (awarded) score wins, mismatch not flagged (no events).
- 4127429 (2023, Naftan Novopolotsk–FC Smorgon): JSON "3 - 0",
  awarded; event feed shows 2-2 played — header (awarded) score
  wins, mismatch flagged.
- 4432693 (2024, Isloch–Dynamo Brest): JSON "1 - 1", round 1,
  event goals 1-1, HT goals 1-0 — matches index and CSV.
