# Preprocessing — Malaysia Liga Super

`data/build_data.py` reads the index and payload JSONs and requires the warehouse base as its first argument. It writes one row per indexed payload to `data/my_ligasuper_matches.csv`, sorted by date and match ID.

FT goals come from the finished payload header score and team scores. Goal events are used for inventory and score reconciliation only. First-half goals count Goal events with `time <= 45`; second-half goals count events with `time > 45`. For awarded or eventless matches, half fields are blank. No field is imputed.

The awarded match is retained with `is_awarded=1`, noted explicitly, and excluded from every later fit and score. Team IDs are the identity keys. `phase` is always `regular`; season labels are copied from the warehouse index.

## Reconciliation

| Check | Result |
|---|---:|
| Payload/index rows | 793 |
| Season counts | 132 / 132 / 182 / 156 / 156 / 35 |
| Model counts | 132 / 132 / 182 / 155 / 156 / 35 |
| Awarded matches | 1 |
| Non-awarded score/event mismatches | 0 |
| HT disagreements | 0 |
| Finished rows with parseable score | 793 |

The CSV contains match identity, season/date, canonical team names and IDs, league and round, goals, regular phase, award flag, first/second-half goals, notes, and content-based feed flags/counts for stats, shotmap, referee, events, goals, halves, cards, Yellow, Red, and YellowRed.
