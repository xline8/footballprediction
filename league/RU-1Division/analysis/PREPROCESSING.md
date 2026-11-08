# Phase 2 — Preprocessing

`data/build_data.py` reads league id `338` from
`data_enrichment/fotmob_world_index.csv`, resolves each payload path against
`--warehouse-root`, and writes one match row plus two team rows per match.
The builder asserts 1,756 source rows.

The full-time score comes from `header.status.scoreStr`. The season label is
retained exactly, and phase is frozen to `regular`. Stats values remain
nullable; no zero filling is performed. The builder keeps the sibling schema,
including expected-goals and shotmap columns, because those fields are absent
here. `fh_` and `sh_` columns are retained for schema parity and are null
because every payload has only `Periods.All`.

First-half goals come from goal events with event time at most 45. A `45+x`
event uses the main event minute 45 and is assigned to the first half; a
`90+x` event is not. Event cards count direct Yellow plus YellowRed for the
yellow target, with YellowRed also counted as a red dismissal. Stats
`yellow_cards` is absent in all 1,756 rows, so `cards_source` is `events` in
every row.

The script does not fit models, create preregistration files, use standings,
h2h, attendance, lineups, or post-match form. Later features must use only
matches strictly before kickoff and ratios of sums where applicable.
