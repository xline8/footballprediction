# EDA — Brazil Série C

All descriptive levels use finished matches; fit-set analyses exclude Final
legs. Virgin 2026 is included for descriptive season levels only.

| season | n | goals/match | OU2.5 over | H / D / A |
|---|---:|---:|---:|---:|
| 2021 | 149 | 2.128 | .349 | .450 / .315 / .235 |
| 2022 | 216 | 2.319 | .449 | .514 / .264 / .222 |
| 2023 | 216 | 2.153 | .366 | .463 / .306 / .231 |
| 2024 | 216 | 2.417 | .444 | .495 / .296 / .208 |
| 2025 | 216 | 2.000 | .315 | .440 / .329 / .231 |
| 2026 | 216 | 2.259 | .403 | .458 / .287 / .255 |

Pooled home goals are 1.305 and away goals 0.912 per match; goal
variance/mean is 0.986. The 2025 low-goals year (2.00) versus 2024 (2.42)
is material era drift.

For 1,079 matches with known half splits, first-half goals are 1,065 of 2,406,
so the frozen ratio-of-sums share is 0.4426 and the presentation constant is
0.443. Per-match share variance is 0.1271 versus a binomial noise floor of
0.1323, giving true variance −0.0052 (approximately zero): the F3 constant
test passes. Team-level split-half r is −0.37 and is noise.

Across 60 random career-pooled halves, with at least 24 matches/team and 36
teams, goals-for reliability is r=0.411 (SD 0.107) and goals-against is
r=0.143 (SD 0.121). The against trait is weak; no defensive-trait
feature is built on it — the Dixon-Coles architecture fits defence
ratings from scores as usual.

Mover sets are four ex-B and four newcomers at each transition into 2022–2025.
The ex-B IDs are 2022: 162165, 162167, 1626, 7733; 2023: 197429, 197692,
2369, 239132; 2024: 109708, 162176, 298660, 414725; 2025: 104823, 197692,
7817, 8630. Newcomers are 2022: 109708, 165546, 239122, 696928; 2023:
1221708, 1340094, 231931, 47387; 2024: 1221604, 172206, 197695, 581832;
2025: 1116984, 197398, 412808, 509487. Pooled, match-weighted first-C
season deviations from the 1.1157 league mean are ex-B n=346, dGF −0.0405,
dGA −0.0868; newcomers n=340, dGF −0.0627, dGA +0.0667. By transition,
ex-B dGF −0.178/+0.080/−0.103/+0.038 and dGA −0.081/−0.204/−0.054/+0.006;
newcomers dGF −0.155/−0.159/+0.185/−0.149 and dGA +0.061/−0.011/+0.094/+0.114.

| target | buildability | evidence |
|---|---|---|
| Goals | BUILDABLE | score in 1,229/1,229 finished matches; 856 scored dev fit-set matches and 214 virgin 2026 matches |
| SOT | NOT BUILDABLE | stats values 0/1,229; shotmap shots 0 |
| Corners | NOT BUILDABLE | stats values 0/1,229 |
| Cards | NOT BUILDABLE | no valid stable dev target: 2021 none; 2022–2024 no Yellow events; 2025–2026 are fuller but virgin-era only |
| Total shots | NOT BUILDABLE | stats values 0/1,229 and shotmap shots 0 |
