# BNAC Phase-A data

Regenerate with:

```text
/home/hatch/workspace/footballprediction/.venv/bin/python league/AR-PrimeraBNacional/data/build_data.py
```

The builder reads `fotmob_world_index.csv` for league_id `8965` and resolves
the warehouse through `FOTMOB_WAREHOUSE`, repository-local `data_enrichment`,
then `/home/hatch/workspace/footballprediction/data_enrichment`. It writes
`bnac_matches.csv` (3,874 group-phase matches) and `team_matches.csv` (7,748
team-match rows). CSVs are regenerable and gitignored.

The inventory reconciliation is 3,966 index rows = 3,874 group rows + 92
playoffs, with per-season group counts 578 / 666 / 648 / 722 / 612 / 648
(2021–2026). Match rows are chronological by `(date, match_id)` and keyed by
FotMob team id.

Full-time scores come from the header. Half-time goals and first-half yellow
fields (`ht_yellow_home`, `ht_yellow_away`) count event-feed events with
integer `time <= 45`; only `card='Yellow'` is a yellow. `YellowRed` and `Red`
are separate red categories. Card columns are NaN before the complete 2023
feed, never zero. Stats and shotmap are asserted empty at payload level; the
121 index `has_stats=True` rows with
`Periods.All=None` are treated as false positives.
The matching team rows expose these as `ht_yellow_for` and
`ht_yellow_against`.
