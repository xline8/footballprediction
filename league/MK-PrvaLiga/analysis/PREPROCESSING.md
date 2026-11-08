# Preprocessing — MK-PrvaLiga

`data/build_data.py` reads the index and payload JSONs, asserts the league identity and finished status, and writes one row per payload to `mk_prva_liga_matches.csv`. It requires the warehouse base as its first argument.

FT goals come from `header.status.scoreStr` and the two header team scores. Goal events are counted only for inventory and validation. First-half goals count Goal events with `time <= 45`; second-half goals count Goal events with `time > 45`. For awarded matches, both half fields are blank. For event-less matches they are blank. No field is imputed.

Awarded matches are retained, marked `is_awarded=1`, and excluded from every model fit and score. Team IDs are the keys. `phase` is always `regular`; the league is a single table. Season labels are copied from the warehouse index.

## Reconciliation

| Check | Result |
|---|---:|
| Payload/index rows | 1,022 |
| Season counts | 198 / 165 / 198 / 198 / 198 / 65 |
| Model counts | 198 / 165 / 198 / 186 / 197 / 65 |
| Awarded matches | 13 |
| Non-awarded score/event mismatches | 0 |
| HT disagreements | 0 |
| Finished rows with parseable score | 1,022 |

Columns include match identity, season/date, team names and IDs, league and round, goals, regular phase, award flag, first/second-half goals, notes, and feed inventory fields: stats, shotmap, named referee, events, goals, halves, cards, yellow, red, and yellow-red counts.
