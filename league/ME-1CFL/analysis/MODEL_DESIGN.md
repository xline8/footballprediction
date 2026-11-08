# Model design — Montenegro 1. CFL

This is the no-fitting design freeze. Only **G-ME (goals)** is buildable.
S-ME has no SOT target (shotmap shots list empty on all 971 rows);
C-ME has no corners (no stats feed); K-ME has no yellow-card target
(no stats feed, and the event feed carries zero Yellow events in 971
matches); T-ME has no total-shots target (no shotmap shots, no stats).
X2 is not a candidate because no Montenegrin sibling league exists in
the warehouse.

## G-ME

G-ME follows the production Dixon-Coles pattern: 14 update sweeps, damping
0.7, +0.25 smoothing, fitted home advantage initialized at 0.28, rho grid
0/−0.05/−0.10/−0.15 selected by weighted goals log-likelihood, score matrix
to MAXG 10 with tau correction, goals-only observations, and frozen 270-day
decay half-life. No fitting is performed in this brief.

Pre-registered arms for the next brief are Gate Zero and **SHRINK**: ratings
are multiplied by `min(1, matches/6)` for thin-data teams. There is no X2 arm.

Shared frame: seed 2021/2022, dev/eval seasons 2022/2023–2024/2025
(n=539), virgin 2025/2026 (n=180, complete), and 2026/2027 reserved
as the future confirmatory season (in progress, 73 rows). The primary
dev line is OU2.5 because its over-rate (0.4453) is closest to 0.5.

One EDA caution carried into the build (F2): team attack traits exist
(season-parity split-half r=0.69) but drift hard within careers
(chronological split-half GF r=0.13). The frozen 270-day decay is the
architecture's answer to that drift; no additional decay search is
pre-registered, and the dev gate is the arbiter.

## GATE LEGS (frozen)

Dev gate — pooled dev 1X2 LL and RPS of an arm must beat climatology, and
OU2.5 LL must beat the base-rate baseline, else the arm is dead. Virgin legs
— (i) LL leg: arm's virgin 1X2 LL ≤ Gate Zero's AND ≤ climatology's; (ii)
calibration leg: |actual − mean predicted| ≤ 1.0pp pooled for home-win rate
and for OU2.5 over-rate, SEs reported; a breach within 1 SE of the boundary
is recorded PROVISIONAL PASS, beyond it FAIL; (iii) per-season sign check on
dev (arm LL ≤ Gate Zero LL in at least half the dev seasons) for the both-pass
rule. Both-pass rule: if Gate Zero and a variant both pass all legs, the lower
pooled virgin 1X2 LL ships; if only one passes, it ships; if none passes,
G-ME verdict is FAIL and nothing ships.

Halves are FT-only unless F3's frozen 0.426643 constant is used for
presentation; it is never fitted.
