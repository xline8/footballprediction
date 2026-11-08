# Model design — NZ-Championship

## Feasibility

G-NZ is the only candidate. S-NZ, C-NZ and T-NZ have no target in any
season: SOT, corners and total shots are absent from stats (0/221)
and shotmaps are present-but-empty on 221/221. K-NZ has no yellow
target: stats are absent and the event feed contains only
Red/YellowRed, never plain Yellow. This is a design verdict, not a
deferral.

## G-NZ

Reference Gate Zero is the production Dixon–Coles goals-only pattern
seeded from `league/IS-1Deild/engine/goals/dc.py`: 14 sweeps, damping
0.7, +0.25 smoothing, h initial 0.28, rho grid (0.0, -0.05, -0.10,
-0.15), 270-day decay half-life and MAXG 10. There is no xG anywhere,
so the goals-only fallback is always used.

The pre-registered arms are:

- Gate Zero: unmodified reference; unseen teams start at the league
  mean.
- SHRINK: ratings shrunk toward the league mean by min(1, count/6),
  where count is the team's training-window match count.

There is no X2 arm: no sibling league exists, so no mover offset can
be estimated.

Expected SHRINK diagnostic (to be confirmed by the harness, not
assumed): with season-blocked fits, the only team with a
training-window count below 6 is Miramar Rangers (5 matches in
2022), and Miramar plays no match in either dev season (absent
2023–2024), so SHRINK is expected to be bit-identical to Gate Zero
across dev. It is retained anyway as the thin-data treatment, and it
would differ on virgin matches involving Miramar (10 matches in
2025) if an arm reaches the virgin read.

Seed is 2022 for training (n=38 played). Dev is season-blocked
walk-forward over 2023–2024, n=92. Virgin is 2025, n=56 and complete.
2026 is in progress (rounds 1–7, 35 matches) and is NOT a virgin
window; it is reserved as a future confirmatory read only. The
primary line is OU2.5 with frozen dev over-rate 0.75; 1X2 LL and RPS
are also primary metrics.

Gate legs are frozen in `prereg/PREREG_G_NZ.md`: pooled dev 1X2 log
loss and RPS must beat climatology, and dev OU2.5 log loss must beat
the base-rate baseline. Virgin legs require both LL comparisons to
Gate Zero and climatology, calibration within 1.0 percentage point
or within 1 SE provisionally for home-win and OU2.5 over-rate, and
the dev per-season sign check for variants. Both-pass applies; ties
go to the simpler arm. If Gate Zero fails dev, variants are moot and
2025 is not read.

Thin-window limitation (recorded before fitting): seed 38, dev 92,
virgin 56. The virgin calibration SEs are ≈5.8pp for the OU2.5
over-rate (p≈0.75) and ≈6.7pp for the home-win rate (p≈0.5, worst
case), so a provisional pass is the realistic best virgin outcome
and a clean ≤1pp pass would be largely luck. F2 adds a second
warning: team traits replicate weakly here (GF r=0.2293, GA
r=0.2570), so the ratings have little stable signal to exploit.

Halves are FT plus 1H/2H presentation using 0.4123 only.
