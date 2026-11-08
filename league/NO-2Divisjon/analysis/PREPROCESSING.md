# Step 2 — Preprocessing: NO-2Divisjon

Script: `data/build_data.py` (adapted from the FI reference build +
the IL scores-only precedent). Input: bundle `index_204.csv` (2,158
rows, league_id 204) + the extracted JSON warehouse. Output:
`data/no_matches.csv` (2,158 rows) + `data/no_team_matches.csv`
(4,316 rows).

## Derivation rules (program standard, none negotiable)

- FT score from `header.status.scoreStr`; verified 0 mismatches
  against the index `score` column.
- Rows: only `status.finished` matches are kept — all 2,158 index
  rows are finished, so CSV count == index count (asserted in the
  script). No rows dropped.
- Phase from `general.leagueName`: "2. Divisjon Avd. 1" → `avd1`,
  "2. Divisjon Avd. 2" → `avd2`. Unknown names would map to
  `unknown` (none occur).
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
  flags the 2 matches where event goals ≠ header score (header wins).
- Team table: one row per team-match (home + away), with goals for /
  against and the (empty) stat columns mirrored.

## Spot checks (3 raw JSONs, by hand)

- 3517998 (2021, Alta–Moss): JSON `scoreStr` "3 - 1", leagueName
  "2. Divisjon Avd. 1", round 1 — matches index and CSV.
- 4696521 (2025, Eidsvold TF–Hønefoss): JSON "2 - 1" — matches.
- 5143624 (2026, Rana FK–Tromsdalen): JSON "0 - 4", finished; the
  event feed lists 5 away Goal events (minute 79 duplicated) —
  header wins, mismatch flagged in the CSV.
