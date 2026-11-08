# Verdict — G-IL (IL-LigatHaAl goals): **FAIL (virgin legs)**

Frozen decision: PREREG_G_IL.md (prereg commit
e9dd3b0, branch wip-il-ligataal, before any fitting). Virgin 2025/2026
was read ONCE (n = 240), only because both arms passed the dev gate.

Dev (pooled 2022/2023–2024/2025, n = 720, season-blocked expanding
fit, warm-up 2021/2022):

| Arm | 1X2 LL | RPS | OU2.5 LL | Dev gate |
|---|---|---|---|---|
| Gate Zero | 1.0186 | 0.2091 | 0.6918 | PASS |
| ENTRANT | 1.0115 | 0.2062 | 0.6920 | PASS |
| Climatology | 1.0851 | 0.2337 | 0.6954 | — |
| Naive trailing-10 | 1.0853 | 0.2200 | 0.7283 | — |

Per season, Gate Zero 1X2 LL / RPS / OU2.5 LL: 2022/2023 1.0268 /
0.2055 / 0.6982; 2023/2024 1.0286 / 0.2148 / 0.6926; 2024/2025
1.0003 / 0.2070 / 0.6847. ENTRANT: 2022/2023 1.0122 / 0.2003 /
0.7016; 2023/2024 1.0261 / 0.2133 / 0.6909; 2024/2025 0.9961 /
0.2051 / 0.6835. Both arms beat both baselines on all three pooled
metrics. ENTRANT beats Gate Zero on pooled 1X2 LL and RPS, and its
leg (iii) sign check passes 3 of 3 dev seasons (ENTRANT 1X2 LL ≤
Gate Zero in 2022/2023, 2023/2024 and 2024/2025).

Virgin 2025/2026 (n = 240, fit on all matches ≤ 2024/2025; rho −0.05,
home advantage 0.1669, 18 teams rated):

| Arm | 1X2 LL | RPS | OU2.5 LL | Leg (i) | Leg (ii) |
|---|---|---|---|---|---|
| Gate Zero | 1.0623 | 0.2242 | 0.6963 | FAIL | FAIL |
| ENTRANT | 1.1173 | 0.2385 | 0.6926 | FAIL | FAIL |
| Climatology | 1.0812 | 0.2329 | 0.6994 | — | — |
| Naive trailing-10 | 1.0238 | 0.2093 | 0.7525 | — | — |

Leg (i) — LL: Gate Zero's virgin 1X2 LL (1.0623) beats climatology
(1.0812) but loses to naive trailing-10 (1.0238), so it fails the
leg's "≤ each baseline" condition; its OU2.5 LL (0.6963) beats both
baselines, but the leg needs both lines. ENTRANT's virgin 1X2 LL
(1.1173) and RPS (0.2385) are worse than Gate Zero and worse than
both baselines; only its OU2.5 LL (0.6926) beats the baselines.
Leg (ii) — calibration: home-win gap +0.65pp (Gate Zero) / +0.94pp
(ENTRANT), both PASS clean (mean predicted home-win 0.4106 / 0.4136
vs actual 0.4042). OU2.5 over-rate gap **−11.70pp** (Gate Zero) /
**−11.16pp** (ENTRANT), both FAIL: mean predicted over-rate 0.4330 /
0.4384 vs actual 0.5500, a gap far beyond 1.0pp + 1 SE (SE ≈ 3.15pp).

Diagnosis (recorded, not acted on): the flagged scoring-level rise
materialised — virgin goals/match 2.967 vs dev scored mean 2.656
(+0.31), and the virgin OU2.5 over-rate 0.5500 vs dev 0.4875. The
pre-season-fitted DC ratings under-predict virgin totals by ~11–12pp
on the over-rate, which breaks both the OU calibration leg and, via
the score matrix, the 1X2 LL leg against the trailing-10 baseline —
the naive baseline adapts inside the virgin season (its trailing-10
feeds on virgin matches as they happen) while the DC fit is frozen
pre-season. ENTRANT's dev advantage does not survive the virgin:
its entrant offsets (frozen from dev transitions) hurt on the virgin
season's entrants. Nothing ships for G-IL.
