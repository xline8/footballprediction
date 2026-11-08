# PE-Liga1 data

`build_data.py` regenerates `pe_liga1_matches.csv` (1,860 rows) and
`pe_liga1_team_matches.csv` (3,720 rows) from the FotMob world
warehouse (league_id 131). The CSVs are gitignored; the builder is
the committed artefact. Counts are asserted as floors. See
`analysis/DATA_UNDERSTANDING.md` (step 1) and
`analysis/PREPROCESSING.md` (step 2) for the corpus rules.
