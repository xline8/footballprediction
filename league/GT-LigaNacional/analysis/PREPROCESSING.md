# Preprocessing and source rules

`data/build_data.py` reads the index with `FOOTMOB_WORLD_ROOT`, worktree-local
warehouse, then main-checkout fallback resolution. It includes only payloads
whose `header.status.finished` is true and writes 1,443 rows sorted by UTC
index date and match ID.

- Header team IDs, names, scores, and index season/date are retained.
- Half-time values come from goal events only. Missing events never become
  fabricated 0-0 half-time values.
- Stats, shotmap, period-split, xG, lineup, referee, and card fields are
  measured from payload content, not copied from index flags.
- `event_yellows_*` counts only `type=Card, card=Yellow`; this corpus has none.
  `event_cards_total` counts all `type=Card` events, which are red or
  second-yellow records.
- The header score is authoritative for FT goals because seven event/header
  mismatches were observed in the cross-check.

Phase A performs no model fitting. Descriptive EDA may include every season,
but no model purpose reads virgin or confirmatory rows.
