# NL Tweede Divisie — preprocessing

Builder: `league/NL-TweedeDivisie/data/build_data.py`, producing
`nl_tweede_matches.csv` (1,638 rows) and `team_matches.csv` (3,276
rows). Data CSVs are gitignored by repo norm; the builder script is
committed so the CSVs are reproducible.

## Inclusion rules

- Played matches only: every index row for FotMob id 9195 with
  `general.leagueName == "Tweede Divisie"` and `header.status.finished
  == True`. 1,638 rows in, 1,638 rows out, 0 excluded by name, 0
  unfinished. Season labels are exactly as in the warehouse
  (`2021/2022` … `2026/2027`).
- Regular season only by construction: the feed contains rounds
  1–34 and no play-off rows.

## Column rules

- FT goals: `header.status.scoreStr` (source of truth); cross-checked
  against goal-event counts — 0 mismatches in 1,638.
- HT goals: derived from goal events (`time <= 45`, credited side),
  via `jleague_lib.ht_from_events`. The 53 matches with an empty
  event feed are all 0-0; their HT is recorded as (0, 0) with
  `ht_source = "events-zero"` (not fabricated: a 0-0 FT with no goal
  events has HT 0-0 by the same feed). All other matches have
  `ht_source = "events"`. No match has `ht_source = "none"`.
- Stats / xG / shotmap columns: present in the CSV schema (same
  column spirit as the sibling Dutch builders) and NaN/0 throughout,
  because the payloads carry none. They are retained as explicit
  absence, not dropped, so a future feed change is visible rather
  than silent.
- Cards: `yellow_*` = 0 everywhere (no Yellow events exist);
  `red_*` = Red + YellowRed event counts per side (238 total,
  0.145/match). `cards_source = "events-red-only"`.
- Referee: empty string in all 1,638 rows (the payload field exists
  but its text is blank).
- Team identity keyed on FotMob team id; names carried for display.
- No imputation anywhere. No row is dropped for missing stats —
  missingness is the corpus, not a defect in a row.

## Split-source rules

- Period splits exist nowhere (no stats feed), so no per-half stat
  is derived except HT goals from events, as above.
- The team_matches table is a mechanical long-form expansion of the
  match table (one row per team per match); `_against` columns are
  the opponent's values from the same row.
