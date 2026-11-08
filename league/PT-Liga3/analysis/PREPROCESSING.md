# Preprocessing and source rules

`data/build_data.py` reads the index with a worktree-first and
main-checkout fallback, resolves each JSON, includes only rows whose
`header.status.finished` is true, and writes 1,647 finished matches sorted by
UTC index date and match ID.

- Header team IDs, names, scores, and index season/date are retained.
- Half-time values are recovered from goal events only; missing values stay blank.
- `has_stats`, `has_shotmap`, `has_period_splits`, xG presence, lineup presence,
  referee text, and shot count are payload-measured, not copied from index flags.
- Event yellows (`type=Card`, `card=Yellow`) and all Card events are separate.
  Stats yellows are never filled from events.
- Five unstarted 0-0 payload shells are excluded because `finished=false`.

There are 0 matches with both a stats block and a Card event, 0 stats-yellow
matches, and therefore a stats-vs-events validation sample of n=0. Agreement,
mean difference, and a 4.5 disagreement count are not estimable.
