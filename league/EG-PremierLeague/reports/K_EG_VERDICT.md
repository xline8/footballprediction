# Verdict — K-EG (Egypt Premier League cards) — **FAIL** (dev gate, naive leg; virgin NOT read)

Prereg: `prereg/PREREG_K_EG.md` (frozen 6b86220, before fitting).
Dev = per-match walk-forward, warm-up 2021/2022, scored
2022/2023–2024/2025 (n = 824 with target). Target = stats-feed
yellows (event feed largely absent before 2024/2025 — EDA F6).
Gate Zero only (X8 dropped in FEATURES: referee r = 0.290,
virgin referee coverage 26.7%). Primary line 3.5.

## Dev (LL@3.5)

| Season | Model | League base rate | Naive trailing-10 |
|---|---|---|---|
| 2022/2023 | 0.8268 | 0.8179 | 0.8495 |
| 2023/2024 | 0.7450 | 0.7506 | 0.7014 |
| 2024/2025 | 0.6995 | 0.7201 | 0.7062 |
| **Pooled** | **0.7624** | **0.7668** | **0.7565** |

Gate arithmetic: pooled model LL beats the league base rate
(0.7624 < 0.7668 ✓) but does **not** beat naive trailing-10
(0.7624 > 0.7565 ✗). The dev gate requires both → FAIL. The
2023/2024 season carries the failure (model 0.7450 vs naive
0.7014): EG's yellows level rose steeply across the dev era
(2.12 → 3.28 → 3.88 → 3.87 per match) and the recent-era
yellows-for trait reliability is weak (split-half r = 0.262 on
2023/2024–2024/2025), so team ratings add less than the naive
trailing mean they are blended with.

## Virgin

**NOT read.** Gate Zero failed the dev gate, per the frozen
mechanical reading; no virgin rows were scored, no fitted params
or predictions written.

**Ships: nothing.** K-EG is a complete FAIL.
