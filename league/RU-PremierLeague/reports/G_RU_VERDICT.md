# Verdict — G-RU (RU-Premier League goals)

**FAIL at the dev gate. Virgin NOT read. Nothing ships.**

Prereg: `prereg/PREREG_G_RU.md` (frozen before fitting). Dev =
walk-forward, seed 2021/2022, scored 2022/2023–2024/2025 (n = 720).
All numbers below were recomputed by the coordinator from the
per-match dev predictions CSV and match `results_dev.json` exactly.

## Dev results (pooled, n = 720)

| arm | 1X2 LL | RPS | OU2.5 LL |
|---|---|---|---|
| Gate Zero | 1.0178 | 0.2092 | 0.7120 |
| SHRINK | 1.0178 | 0.2092 | 0.7120 |
| climatology | 1.0675 | 0.2268 | 0.6975 |

Per-season OU2.5 LL (model vs climatology): 2022/2023 0.7388 vs
0.6894; 2023/2024 0.7186 vs 0.7084; 2024/2025 0.6785 vs 0.6947.
Per-season 1X2 LL (model): 1.0173 / 1.0539 / 0.9823 — the model
beats climatology on 1X2 LL and RPS pooled and in every season.

## Gate arithmetic

Dev gate (verbatim): pooled 1X2 LL and RPS must beat climatology
AND OU2.5 LL must beat the base-rate baseline. 1X2 leg: 1.0178 <
1.0675 PASS. RPS leg: 0.2092 < 0.2268 PASS. OU leg: 0.7120 >
0.6975 **FAIL**. Gate Zero therefore fails its own dev gate;
per the prereg's mechanical reading the SHRINK variant is moot
(it is in any case identical to Gate Zero on every scored match —
under season-blocked fitting no team ever sits in the 1–5 prior
match band, the recorded finding the prereg anticipated) and the
virgin is NOT read.

The OU failure is driven by 2022/2023, the one-season goals
excursion (3.042 goals/match after 2.663): a DC fit on pre-season
data under-prices totals for a full season, and the pooled OU leg
never recovers. This is a level-shift failure of the totals leg,
not of the 1X2 ratings.

## What ships

Nothing. No fitted params, no predictions. G-RU is closed as FAIL;
2026/2027 remains the reserved confirmatory window, unread.
