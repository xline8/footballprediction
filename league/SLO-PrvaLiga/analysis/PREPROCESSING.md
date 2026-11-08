# Preprocessing — SLO-PrvaLiga

`data/build_data.py` reads the index and payload JSONs, asserts the league identity and finished status, and writes one row per payload to `slo_prva_liga_matches.csv`. It requires the warehouse base as its first argument.

FT goals come from `header.status.scoreStr` and the two header team scores. Goal events are counted only for inventory and validation. First-half goals count Goal events with `time <= 45`; second-half goals count Goal events with `time > 45`. For awarded or eventless matches, both half fields are blank. No field is imputed.

Awarded matches are retained, marked `is_awarded=1`, and excluded from every model fit and score. Team IDs are the keys. `phase` is always `regular`; the league is a single table. Season labels are copied from the warehouse index.

## Reconciliation

| Check | Result |
|---|---:|
| Payload/index rows | 956 |
| Season counts | 180 / 180 / 180 / 180 / 162 / 74 |
| Model counts | 180 / 180 / 178 / 180 / 161 / 74 |
| Awarded matches | 3 |
| Non-awarded score/event mismatches | 0 |
| HT disagreements | 0 |
| Finished rows with parseable score | 956 |

Columns include match identity, season/date, team names and IDs, league and round, goals, regular phase, award flag, first/second-half goals, notes, and feed inventory fields: stats, shotmap, named referee, events, goals, halves, cards, yellow, red, and yellow-red counts.
