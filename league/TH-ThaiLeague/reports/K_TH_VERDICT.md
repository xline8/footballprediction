# Verdict — K-TH (cards): **FAIL**

Prereg: `prereg/PREREG_K_TH.md` (frozen and committed before fitting).
Primary line 4.5; target = stats-feed yellows (frozen target-source
decision in the prereg: the dev-era event feed publishes no plain-yellow
events, so no event-unified dev target exists). All numbers recomputed
by the coordinator from the per-match dev CSV against the league CSV
(0 target mismatches).

## Dev (seed 2022/2023; scored 2023/2024–2024/2025, n = 480)

| Arm | Pooled LL@4.5 | 2023/2024 | 2024/2025 |
|---|---|---|---|
| Gate Zero | 0.7022 | 0.7349 | 0.6696 |
| League base rate | 0.7113 | — | — |
| Naive trailing-10 | 0.6977 | — | — |

## Gate arithmetic

Dev gate requires pooled LL@4.5 to beat BOTH baselines. Gate Zero beats
the league base rate (0.7022 < 0.7113) but **loses to naive trailing-10
(0.7022 > 0.6977)**. Gate Zero fails its dev gate; the **virgin was NOT
read**, and the preregistered virgin event-unified sensitivity —
conditional on a dev-passing arm being read on the virgin — was
therefore not computed either.

**K-TH FAILS. Nothing ships.**
