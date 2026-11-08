# Phase 1 — EDA

eda_compute.py writes the reproducible result to eda_numbers.json; make_charts.py writes the BE-style levels, reliability, and halves charts.

The played-match levels are goals 2.654–3.048, SOT 8.516–9.515, corners 9.394–9.724, total shots 25.337–27.798, and stats yellows 3.561–4.654 across seasons. Home goals exceed away goals in every season. Per-season coverage for every consumed stat key is recorded in the JSON.

## Cards decision

On the four DEV seasons only (n=1,413 matches with stats cards), stats versus event total yellows agree exactly in 84.9%; stats are lower in 14.4%, higher in 0.7%, and the mean difference is −0.241 per match. The stats feed is therefore the unified target; event counts are audit-only. Including YellowRed in the event count gives 84.6% agreement and a −0.352 mean difference.

## Reliability method

For each season and pooled corpus, team traits use 60 random split-halves, career/season pooled by team, with a minimum of 20 team matches; ratio traits use ratio-of-sums. Referee strictness is total unified yellows per referee, with the season table using at least five appointments and the pooled check at least 20. The full reliability_by_season table is machine-readable.

Pooled reliabilities that drive feature choices are: goals for/against 0.812/0.593; SOT for 0.830; corners for 0.693; shots for 0.854; cards for 0.350; xG for 0.855; xG/shot 0.436; set-play-xG share 0.401; box touches for/against 0.877/0.775; referee strictness 0.505 (30 referees); and xGOT/shot 0.292 in the near-universal era. XGOT populated-shot coverage is 40.9%, 34.6%, 33.5%, then 99.5%, 99.7%, 99.7%, so it is not valid before 2024/2025.

## Halves

The complete-splits DEV era is exactly 2023/2024 + 2024/2025. Mean first-half shares are goals 0.4403, SOT 0.4435, corners 0.4801, total shots 0.4544, and yellows 0.3428. The true-variance checks are approximately zero for goals, SOT, and shots; corners is 0.0015 and yellows 0.0072. These are frozen report constants, not team features.
