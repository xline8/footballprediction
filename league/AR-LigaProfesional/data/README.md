# AR Liga Profesional data

`build_data.py` reads `data_enrichment/fotmob_world_index.csv` from the repository root and the per-match JSON warehouse paths in that index. It retains group-phase matches (round-robin 2021–2024; Apertura/Clausura group rounds 2025–2026); the 45 playoff-bracket rows are excluded by the round/leagueName rule documented in the builder.

Run from the worktree root with:

```bash
~/workspace/footballprediction/.venv/bin/python league/AR-LigaProfesional/data/build_data.py
```

Outputs are `ar_matches.csv` (2,419 matches) and `team_matches.csv` (4,838 team-match rows). The run reconciled 2,464 league-112 index rows as 2,419 group-phase rows plus 45 excluded playoffs, with unique match IDs and two team rows per match. `touches_opp_box` was present in the stats feed and is included. The unified yellow target (`yellow_*`) is event-derived in this league; the raw stats-feed value is kept in `yellow_cards_*` (see `../analysis/PREPROCESSING.md` rule 5).
