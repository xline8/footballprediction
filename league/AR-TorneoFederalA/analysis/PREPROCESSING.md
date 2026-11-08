# Preprocessing

`data/build_data.py` resolves the warehouse through `FOTMOB_WAREHOUSE`, a complete repository-local warehouse, then the shared footballprediction warehouse. It filters parent id 9213 to `general.leagueName` beginning `Federal A`, requires a finished two-team header score, and writes one row per group-phase match.

The inclusion rule retains first-phase zones and ordinary second-phase Promotion/Relegation Zona rows. It excludes any tournament name containing Playoff, Championship Playoff, Relegation Playoff, or Additional match. Header FT goals are authoritative. Event goals are used only to derive first-half goals, using event time <=45; halves are NaN for the ten mismatches or for matches without events. The CSV carries `phase` and `zone` so second-phase levels are not mixed invisibly with first-phase levels.

Team identity is the header team id, with the latest observed spelling as canonical name. The CSV is regenerated, not hand-maintained, and is intentionally gitignored.
