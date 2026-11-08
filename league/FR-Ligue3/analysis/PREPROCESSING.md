# Step 2 — Preprocessing: FR-Ligue3

Script: `data/build_data.py` (adapted from the NO-2Divisjon
scores-only build). Input: bundle `index_8970.csv` (1,570 rows,
league_id 8970) + the extracted JSON warehouse. Output:
`data/fr_matches.csv` (1,570 rows) + `data/fr_team_matches.csv`
(3,140 rows).

## Derivation rules (program standard, none negotiable)

- FT score from `header.status.scoreStr`; verified 0 mismatches
  against the index `score` column.
- Rows: only `status.finished` matches are kept — all 1,570 index
  rows are finished, so CSV count == index count (asserted in the
  script). No rows dropped.
- Phase from `general.leagueName`: "National" → `main`,
  "Ligue 3" → `main` (single group every season). Unknown names
  would map to `unknown` (none occur).
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
  flags the 6 matches where event goals ≠ header score (5 awarded +
  4879591 duplicated Goal event; header wins).
- Team table: one row per team-match (home + away), with goals for /
  against and the (empty) stat columns mirrored.

## Spot checks (3 raw JSONs, by hand)

- 4247769 (2023/2024, Nancy–Dijon): JSON `scoreStr` "3 - 0",
  leagueName "National", round 6, 18 events, stats Periods empty,
  shotmap 0 — matches index and CSV.
- 3955519 (2022/2023, Concarneau–Orleans): JSON "0 - 3", awarded;
  event feed shows 1-1 played — header (awarded) score wins, mismatch
  flagged.
- 4247903 (2023/2024, Martigues–Epinal): JSON "2 - 1", round 23 —
  matches index and CSV.
