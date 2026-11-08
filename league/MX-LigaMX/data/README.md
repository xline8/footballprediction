# Liga MX Phase A data

`build_data.py` reads the symlinked FotMob warehouse through `fotmob_world_index.csv`; it never copies the warehouse. Run it from the repository root with the project virtualenv Python.

Outputs are regenerable and gitignored: `mx_matches.csv` contains the 1,530 regular-phase matches from ten complete 18-team tournaments, and `team_matches.csv` contains two team-perspective rows per match. Playoff rows are excluded by the frozen `matchRound.isdigit()` rule, and the incomplete 2026/2027 Apertura is excluded entirely.

The event feed is the unified yellow-card target. The stats-feed `yellow_cards_*` values are retained for agreement diagnostics. Shotmap aggregates count regulation shots only; stadium city and referee are retained for EDA. The builder prints a JSON summary with counts and dev-era card agreement.
