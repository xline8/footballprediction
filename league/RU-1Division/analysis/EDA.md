# Phase 3 — EDA: RU-1Division

All reported figures are emitted by `eda_compute.py` into `eda_numbers.json`.
No model is fitted.

| season | n | goals | home | away | home adv. | SOT | corners | total shots | event yellows |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2021/2022 | 380 | 2.513 | 1.353 | 1.161 | 0.192 | 8.271 | 9.345 | 17.408 | 5.845 |
| 2022/2023 | 306 | 2.297 | 1.284 | 1.013 | 0.271 | 6.163 | 8.147 | 13.712 | 4.768 |
| 2023/2024 | 306 | 2.190 | 1.261 | 0.928 | 0.333 | 7.330 | 9.149 | 14.833 | 3.614 |
| 2024/2025 | 306 | 2.167 | 1.216 | 0.951 | 0.265 | 7.655 | 8.900 | 14.533 | 3.663 |
| 2025/2026 | 305 | 2.321 | 1.292 | 1.030 | 0.262 | 7.847 | 9.080 | 14.868 | 3.970 |
| 2026/2027 | 153 | 2.680 | 1.497 | 1.183 | 0.314 | 7.924 | 9.386 | 14.855 | 4.229 |
| pooled | 1,756 | 2.340 | 1.303 | 1.037 | 0.266 | 7.522 | 8.980 | 15.175 | 4.422 |

## Coverage and cards

Stats All coverage is 100.0%, 100.0%, 94.1%, 85.3%, 94.1%, and 94.8% by
season. The four available keys have the same coverage in this feed:
possession, total shots, SOT, and corners. Events are 100.0% in every season;
referee and shotmap coverage are 0.0% in every season. Stats
`yellow_cards` is absent in all 1,756 rows. The cards artefact comparison is
therefore moot: there are no stats-card rows to compare. The target is event
yellows by construction.

## Reliabilities

Career-pooled random split-half correlations, with team counts in the JSON,
are: goals for/against 0.609/0.637; SOT for/against 0.673/0.633; corners
for/against 0.612/0.661; total shots for/against 0.751/0.714; event yellows
for/against 0.722/0.724; and possession for/against 0.844/0.839.

## Primary lines

The dev period is the seed plus scored seasons 2021/2022–2024/2025, with
1,298 event-card/goals observations and 1,235 stats observations where the
relevant stat exists. Nearest-to-0.5 over-rates select SOT 7.5 at 0.466,
corners 8.5 at 0.530, event yellows 4.5 at 0.461, total shots 15.5 at 0.512,
and goals OU 2.5 at 0.414. (Coordinator correction after audit: the first
total-shots grid, 23.5–26.5, was transplanted from RU-Premier, whose level
is ~25/match; this league's total-shots level is ~15/match, so the grid was
re-run over 13.5–16.5 before any fitting and 15.5 selected. The feed's
total_shots counts in this league run far below the RU-Premier feed's —
SOT/total-shots ≈ 0.50 here vs ≈ 0.33 there — a feed-definition quirk of
this division, recorded as found; the target is the feed value as-is.)

## Halves and invasion era

The event-derived goals first-half constant is 0.4599 across 1,415 matches
with at least one goal in 2021/2022–2025/2026. `45+x` is assigned to the first
half because the event's main time is 45; `90+x` is second half. Observed
per-match share variance is 0.12752 versus binomial noise expectation 0.12939,
for a noise ratio of 0.986 and true variance of -0.00187. This is consistent
with binomial noise. SOT, corners, cards, and total shots are FT presentation
only because no period splits exist.

The 2021/2022 pre/post-2022-02-24 split has 250/130 matches and goals of
2.452/2.631. The later season levels are 2.297, 2.190, 2.167, 2.321, and
2.680 goals per match. The first-half split is descriptive; the season path
does not establish a persistent invasion-era break.

## X2 movers

The parent-tier comparison uses the RU-Premier corpus logic in memory, with
1,312 parent rows. Relegated-from-RU-Premier movers are n=9: their prior
RU-Premier GF/GA per match averages 0.941/1.707, and their first-season
RU-1Division GF/GA gap is +0.233/-0.126. Promoted-second-tier-or-other is
n=11 with first-season GF/GA gap -0.136/+0.059. Returning is n=3 with gap
-0.139/+0.087. Individual mover records, including each prior-season
RU-Premier performance and each season's league gap, are in the JSON. The
evidence supports a goals shrinkage arm, but not a hard-coded common offset.
