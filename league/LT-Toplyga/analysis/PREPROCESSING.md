# Lithuania Toplyga — preprocessing

Run `python3 league/LT-Toplyga/data/build_data.py`. It writes one match row
per finished warehouse payload and two team rows per match. The script asserts
1,044 total rows and season counts 180/180/180/180/180/144.

- FT goals come from official `scoreStr`, never from events.
- HT goals come from event goals with credited `isHome` and minute ≤45.
  Missing event lists and both awarded mismatches remain blank/flagged.
- `score_events_mismatch` is a provenance flag; no score is silently repaired.
- Season labels are the warehouse folder labels: `2021` through `2026`.
- Team ids are the sole identity key; names are descriptive spellings only.
- Stats, shotmap, lineup, referee and cards are coverage/provenance fields;
  absent feeds are not imputed to zero.
- `lt_team_matches.csv` is a long view with goals, HT values, venue, result,
  points and the awarded flag.

The committed scripts regenerate the CSVs and all headline JSON numbers.
