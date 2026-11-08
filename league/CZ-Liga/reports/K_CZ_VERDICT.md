# Verdict — K-CZ (CZ-Liga cards, event-unified yellows, Gate Zero only)

**FAIL — dev gate (league base-rate leg). Virgin NOT read.
Nothing ships.**

Dev (pooled, n = 810, LL@3.5):

| | LL@3.5 | Dev gate |
|---|---|---|
| Gate Zero | 0.689379 | beats naive ✓, base rate ✗ |
| League base rate | **0.688269** | |
| Naive trailing-10 | 0.691767 | |

Gate arithmetic (PREREG_K_CZ): the dev gate requires LL@3.5 to
beat BOTH baselines. Gate Zero beats the naive (0.691767) but not
the league base rate (0.688269 vs model 0.689379, Δ = +0.001110)
→ **dev gate FAILS**. Per the frozen mechanical reading the virgin
window was NOT read (`engine/cards/results_virgin.json`:
`virgin_read: false`).

Per-season LL@3.5 (model / base / naive): 2022/2023 0.679803 /
0.685327 / 0.712066 (model best); 2023/2024 0.674139 / 0.662406 /
0.658948 (model worst — the season event yellows spiked to
4.61/match, EDA F1, and the trailing ratings lagged it); 2024/2025
0.714194 / 0.717074 / 0.704288. The pooled failure is the
2023/2024 season's doing, but the gate is pooled and does not move.

Context, stated plainly: team yellows-for was the weakest reliable
trait in this league (EDA F2, split-half r = 0.302), and the
model's virgin-era promise was never tested — this is a dev-side
FAIL, complete as it stands. The X8 referee arm was not available
as an alternative: referee names are absent from every dev-era
payload in this league (FEATURES X8), so no variant existed to
register.
