# Phase 2 — Preprocessing

`build_data.py` reads league_id 63 from `data_enrichment/fotmob_world_index.csv`, resolves each `path` against `--warehouse-root` (default `~/workspace/footballprediction`), and writes one match row plus two team rows per match.

Only finished/played index records are in scope. The full-time score is the target source. The season label is the warehouse label, retained exactly. Phase is frozen to `regular` because the inventory has no split/play-off phase.

Stats values are nullable and are never replaced with zero. The production yellow target is stats-feed yellow cards when both sides are available, otherwise event yellows; the raw stats yellow, event-yellow, YellowRed, and red counts are all retained. Events provide first-half goals. First-half stats are used only when the matching Periods block exists.

No fitting, walk-forward evaluation, preregistration, table snapshots, h2h, attendance, lineups, or post-match form is performed in this phase. Later trailing features must use only matches strictly before kickoff, with ratios of sums.

