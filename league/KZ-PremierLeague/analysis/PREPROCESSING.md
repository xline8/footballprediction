# Preprocessing

`data/build_data.py` adapts the UY-SegundaDivision scores-only parser.
It reads the filtered world index (`league_id == 225`), resolves
warehouse-relative JSON paths (against the repo root when it holds the
`fotmob_world` tree, else read-only against the main checkout
`~/workspace/footballprediction` — the 24 GB tree is untracked, so a
git worktree does not contain it), uses header scores/status,
preserves event counts, derives first-half goals from event minutes
`<=45` (cross-validated 1,040/1,040 against the `Half` events' own HT
scores), and canonicalises names by FotMob team ID. Stats and split
columns remain missing with `has_stats_all=False` and
`has_stats_half=False`; unified card targets remain missing because
the event feed has no consistent yellow-card series (zero plain
Yellow events in any season).

Inclusion is finished payloads only (all 1,124 are finished). The
generated [kz_premier_matches.csv](../data/kz_premier_matches.csv)
has 1,124 rows: 182 + 182 + 182 + 156 + 182 + 240. The team-match
file has 2,248 rows. Goals sum to 2,872; season totals are 468, 478,
445, 369, 496, and 616. Event goals agree with scores wherever
events are present except the 4 flagged mismatches (3 awarded, 1
feed-extra goal); empty-event matches retain score-derived goals and
missing event-derived fields.
