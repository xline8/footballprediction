# Model design — Lithuania Toplyga

This is the no-fitting design freeze. Only **G-LT (goals)** is buildable.
S-LT has no SOT target; C-LT has no corners; K-LT has no yellow-card target;
T-LT has no total-shots target. X2 is not a candidate because no sibling
league exists in the warehouse.

## G-LT

G-LT follows the production Dixon-Coles pattern: 14 update sweeps, damping
0.7, +0.25 smoothing, fitted home advantage initialized at 0.28, rho grid
0/−0.05/−0.10/−0.15 selected by weighted goals log-likelihood, score matrix
to MAXG 10 with tau correction, goals-only observations, and frozen 270-day
decay half-life. No fitting is performed in this brief.

Pre-registered arms for the next brief are Gate Zero and **SHRINK**: ratings
are multiplied by `min(1, matches/6)` for thin-data teams. There is no X2 arm.

Shared frame: seed 2021, dev/eval seasons 2022–2025 (n=720), virgin 2026
(n=144, complete), and 2027 reserved as the future confirmatory season.
The primary dev line is OU2.5 because its over-rate is closest to 0.5.

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
G-LT verdict is FAIL and nothing ships.

Halves are FT-only unless F3's frozen 0.43038 constant is used for
presentation; it is never fitted.
