# Phase 5 — Model Design: G-PL-II

One candidate exists: G-PL-II, goals. It follows production
`model_v2.py`, `hl=270`: Dixon–Coles, 14 sweeps, damping 0.7, +0.25
smoothing, fitted home advantage, MAXG=10, production tau, and rho grid
0, −0.05, −0.10, −0.15 by weighted goals LL.

Gate Zero is the goals-only X1 DC. SHRINK is the sanctioned G-J2 arm:
at prediction time, attack and defence are multiplied by n/6 for teams
with fewer than six prior in-league matches (n=0 unchanged). There is no
X2 arm and no other variant.

Dev is season-blocked walk-forward: seed 2021/2022; evaluate
2022/2023–2024/2025, pooled scored n=927. The harness must not read
2025/2026 or 2026/2027. Virgin is 2025/2026 (n=309); 2026/2027 (n=134)
is confirmatory only and is not read. Calibration is actual minus
predicted. Primary line is OU2.5. Parent G-PL failed virgin leg (i);
sibling G-GR2 failed its dev OU2.5 LL leg. No model is fit in Phase A.

Gate legs (frozen; verbatim in `prereg/PREREG_G_PLII.md`): dev gate —
pooled dev 1X2 LL and RPS must beat climatology, and OU2.5 LL must beat
the base-rate baseline, else the arm is dead. Virgin legs — (i) LL:
arm's virgin 1X2 LL ≤ Gate Zero's AND ≤ climatology's; (ii)
calibration: |actual − mean predicted| ≤ 1.0pp pooled for home-win rate
and OU2.5 over-rate, a breach within 1 SE of the boundary is PROVISIONAL
PASS, beyond it FAIL; (iii) per-season sign check on dev for variant
arms. Both-pass rule: if Gate Zero and a variant both pass, the lower
pooled virgin 1X2 LL ships; if only one passes, it ships; if none
passes, G-PL-II is FAIL and nothing ships. If Gate Zero fails its own
dev gate, variants are moot, verdict FAIL, virgin NOT read.
