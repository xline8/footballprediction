# Verdict — G-SK (SK-1Liga goals, Dixon–Coles goals-only)

**FAIL — dev gate (OU2.5 leg). Virgin NOT read. Nothing ships.**

Dev (season-blocked walk-forward; train seed 2021/2022; pooled
n = 576):

| Arm | 1X2 LL | RPS | OU2.5 LL |
|---|---|---|---|
| Gate Zero | **1.030820** | **0.212279** | 0.713626 |
| SHRINK | 1.030820 | 0.212279 | 0.713626 |
| X2 | **1.029469** | **0.211874** | 0.713146 |
| Climatology | 1.076210 | 0.229623 | **0.693351** |

Per-season Gate Zero OU2.5 LL vs climatology: 2022/2023 0.744258
vs 0.693147 ✗; 2023/2024 0.692855 vs 0.693758 ✓; 2024/2025
0.703764 vs 0.693147 ✗. The 1X2 legs pass comfortably in every
season; the OU2.5 leg fails pooled and in 2 of 3 seasons — the
DC lambdas are informative about who wins but their total-goals
level is worse than a constant base rate at the 2.5 line, worst
in 2022/2023 where the fit rests on the single 192-match seed
season.

Gate arithmetic (PREREG_G_SK): the dev gate requires an arm's
pooled 1X2 LL **and** RPS to beat climatology **and** its OU2.5
LL to beat the base-rate baseline. Gate Zero fails the OU2.5 leg
(0.713626 > 0.693351) → Gate Zero is dead; X2 also fails it
(0.713146 > 0.693351), so no variant survives either. SHRINK is
numerically identical to Gate Zero in every season — under the
season-blocked fit every club carries either ≥6 prior matches or
0 (new movers, where SHRINK ≡ the unseen-team rule), so the arm
never separates here. Per the prereg, when Gate Zero fails its
dev gate the variants are moot and the virgin is NOT read:
`engine/goals/results_virgin.json` records
`{"virgin_read": false, "reason": "gate zero failed dev gate"}`
(written by the harness's own guard).

Ships: nothing. No predictions, no fitted params.
