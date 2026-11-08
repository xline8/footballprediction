# NL Eredivisie data

`build_data.py` reads `data_enrichment/fotmob_world_index.csv` from the repository root and the per-match JSON warehouse paths in that index. It retains regular-season matches whose JSON `general.leagueName` is exactly `Eredivisie`; the 21 ECL playoff rows are excluded.

Run from the worktree root with:

```bash
~/workspace/footballprediction/.venv/bin/python league/NL-Eredivisie/data/build_data.py
```

Outputs are `nl_matches.csv` (1,638 matches) and `team_matches.csv` (3,276 team-match rows). The run reconciled 1,659 league-57 index rows as 1,638 regular-season rows plus 21 excluded playoffs, with unique match IDs and two team rows per match. `touches_opp_box` was present in the stats feed and is included. 
