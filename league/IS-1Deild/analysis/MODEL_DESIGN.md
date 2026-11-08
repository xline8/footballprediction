# Model design — IS-1Deild

## Feasibility

G-IS1 is the only candidate. S-IS1, C-IS1 and T-IS1 have no target in any season: SOT, corners and total shots are absent from stats (0/812) and shotmaps (0/812). K-IS1 has no yellow target: stats are absent and the event feed contains only Red/YellowRed, never plain Yellow. This is a design verdict, not a deferral.

## G-IS1

Reference Gate Zero is the production Dixon–Coles goals-only pattern seeded from `league/IS-BestaDeildin/engine/goals/dc.py`: 14 sweeps, damping 0.7, +0.25 smoothing, h initial 0.28, rho grid (0.0, -0.05, -0.10, -0.15), 270-day decay half-life and MAXG 10.

The pre-registered arms are:

- Gate Zero: unmodified reference; movers start at the league mean.
- SHRINK: ratings shrunk toward the league mean by min(1, count/6), where count is the team's training-window match count.
- X2: SHRINK plus direction-specific offsets. A club entering from Besta deildin receives the relegated offset; a club entering from 2. Deild receives the promoted offset. Each offset is estimated only from completed entrant transitions before the target season, using in-corpus GF/GA deviations, and clamped to log(0.8)–log(1.25) per side. A club with no immediately preceding-season record in 216, 215 or 10226 starts at league mean in every arm. Membership is keyed by team ID.

Playoff matches are included in fit and scoring; phase is retained and reported, not used as an additional feature. Seed is 2021 for training. Dev is season-blocked walk-forward over 2022–2025, n=543. Virgin is 2026, n=137 and complete. The primary line is OU2.5 with frozen dev over-rate 0.6814; 1X2 LL and RPS are also primary metrics.

Gate legs are frozen in `prereg/PREREG_G_IS1.md`: pooled dev 1X2 log loss and RPS must beat climatology, and dev OU2.5 log loss must beat the base-rate baseline. Virgin legs require both LL comparisons to Gate Zero and climatology, calibration within 1.0 percentage point or within 1 SE provisionally for home-win and OU2.5 over-rate, and the dev per-season sign check for variants. Both-pass applies; ties go to the simpler arm. If Gate Zero fails dev, variants are moot and 2026 is not read.

Halves are FT plus 1H/2H presentation using 0.4418 only.

