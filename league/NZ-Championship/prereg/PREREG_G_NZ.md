# Preregistration — G-NZ

Frozen before fitting. Seed season is 2022 (n=38 played).
Development is season-blocked walk-forward over 2023 and 2024, n=92
(46+46). The virgin window is complete 2025, n=56. The dev harness
must not read 2025 rows for fitting, selection, or gate setting. 2026
is in progress and is not a virgin window.

The primary lines are 1X2 and OU2.5. The OU2.5 dev over-rate is frozen
from the CSV at 0.75 (69/92; by season 0.7391 in 2023 and 0.7609 in
2024). Climatology is pooled outcome rates and OU2.5 over-rate from
seasons strictly before the target season; the virgin climatology is
pooled 2022–2024.

Arms are limited to two: Gate Zero is the unmodified production
Dixon–Coles goals-only reference (14 sweeps, damping 0.7, +0.25
smoothing, h initial 0.28, rho grid (0.0, -0.05, -0.10, -0.15),
270-day decay half-life, MAXG 10), with unseen teams at the league
mean. SHRINK shrinks ratings toward the league mean by min(1,
count/6), count being the team's training-window match count. There
is no X2 arm (no sibling league exists). Finals are included in fit
and scoring at their 90-minute score.

The dev gate is: pooled dev 1X2 log loss and RPS must beat
climatology, and OU2.5 log loss must beat the base-rate baseline at
0.75. Gate Zero is exempt from the variant sign check. Gate Zero
failure makes SHRINK moot and means the virgin is not read.

An arm passes only if it passes the dev gate and its virgin legs:
(i) LL is no worse than Gate Zero and no worse than virgin
climatology; (ii) pooled home-win rate and OU2.5 over-rate
calibration error is at most 1.0 percentage point for a clean pass,
or within 1 SE for a PROVISIONAL PASS, with SEs reported
(calibration = actual − predicted); (iii) SHRINK passes its dev
per-season sign check (1X2 LL no worse than Gate Zero in at least
half the dev seasons). Both-pass is required. A breach within 1 SE
is PROVISIONAL PASS; otherwise FAIL, with the failed leg named
mechanically. Ties go to the simpler arm: Gate Zero, then SHRINK.
The virgin is read once only for arms passing dev.

Thin-window limitation (recorded before fitting): seed n=38, dev
n=92, virgin n=56. Virgin calibration SEs are ≈5.8pp for the OU2.5
over-rate (p≈0.75) and ≈6.7pp for the home-win rate (p≈0.5, worst
case), so a provisional pass is the realistic best virgin outcome.
