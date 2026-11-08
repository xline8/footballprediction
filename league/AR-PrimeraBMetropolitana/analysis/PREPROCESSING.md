# Phase 2 — Preprocessing

`data/build_data.py` reads `fotmob_world_index.csv` through the required
warehouse fallback chain: `FOTMOB_WAREHOUSE`, a valid repository-local
warehouse, then `/home/hatch/workspace/footballprediction/data_enrichment`.
It filters parent league `9213` to payloads whose `general.leagueName`
contains `Metropolitana`.

Only finished group-phase matches are written. A row is excluded when the
Tournament name (falling back to `general.leagueName`) contains Promotion
Playoff, Championship Playoff, Complemento, or Fase Tercer Ascenso. The
builder asserts the full inventory, season counts, exclusion buckets, score
coverage, zero non-empty stats/shotmap/referee coverage, zero yellow events,
and the absence of header/event goal mismatches.

The CSV uses FotMob team ids as keys and the latest observed spelling as the
canonical team name. Header scores are authoritative. First-half goals are
derived only from Goal event times, with `time <= 45` assigned to 1H. A
non-zero score with an untimed goal would be NaN and is a hard assertion in
this league; no such row exists. Empty event lists on 0–0 rows have zero
first-half goals and `ht_source=none`.

The resulting `data/pbm_matches.csv` has one row per group match. It is
gitignored and reproducible from the builder.
