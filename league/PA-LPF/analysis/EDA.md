# PA-LPF EDA

All results use 688 regular-season matches after awarded exclusion.

| season | n | goals/match | home win | draw | away win | over 2.5 | home GD |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2023 | 120 | 2.542 | .467 | .233 | .300 | .467 | .375 |
| 2024 | 191 | 2.220 | .414 | .288 | .298 | .387 | .147 |
| 2025 | 191 | 2.414 | .372 | .325 | .304 | .424 | .183 |
| 2026 | 186 | 2.699 | .398 | .328 | .274 | .484 | .226 |
| pooled | 688 | 2.459 | .407 | .299 | .294 | .438 | .189 |

Scoring dips in 2024 then rises; home GD stays positive while home-win share
falls from the partial 2023 seed. GF split-half r (2023→2026) is .211, -.078,
.287, .298; GA is .929, .426, .446, .504. There are only 12 teams per block
(13 across 2025), four blocks, and two scored development seasons: small-n
caution applies.

All rows have HT (HT derivation cross-checked against the `Half`
event at minute 45: agreement 626/626 matches that carry events;
the other 64 CSV rows are the event-less 0–0 matches, HT 0–0).
The frozen pooled 1H goal share is **0.449173**; season
shares are .419672, .441038, .438178, .484064. Observed per-match share
variance is .120144 versus binomial expected .125018, i.e. the
estimated true variance is ≤ 0 — per-match 1H share is pure noise
around the constant. Own-goals split-half r (mean over 20 random
splits per season) is .27, .07, .10, .07 for 2023–2026, with
per-season ranges spanning roughly ±0.4; pooled over team-season
blocks r = −0.03 (seed 0). A single-seed pooled r of .42 was also
computed but is null-compatible: 1,000 binomial resamples give null
mean −.004, SD .378, 5–95% [−.62, .63]. This is not signal; retain
only the pooled presentation constant. Match-total shares are
confounded by volume.

No sibling Panama league overlaps target teams. In expanding season blocks,
the only target teams with fewer than 6 prior in-league matches are
brand-new clubs with 0 priors: Veraguas United (target 2024), SD Atletico
Nacional (target 2025), Union Cocle (target 2026) — one per target season,
none with 1–5 priors. X2-SHRINK therefore shrinks only n = 0 teams, for
whom it is identical to Gate Zero's unseen-team rule (a = d = 0): under
this season-blocked walk-forward the SHRINK arm is expected to be
DEGENERATE (byte-identical predictions to Gate Zero), exactly as in AM.
The arm stays pre-registered (it is the sanctioned G-J2-lesson arm) and
the degeneracy is a design note, not an implementation defect — to be
verified from the dev output, not assumed. Feasibility: goals buildable; SOT, corners, yellows, and total
shots are NOT BUILDABLE (0 available). Red inventory is 204, or .296512/match.
The 2023 Apertura gap leaves only 120 seed regular matches.
