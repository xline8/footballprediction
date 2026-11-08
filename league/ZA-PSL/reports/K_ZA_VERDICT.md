# Verdict — K-ZA (cards): **FAIL**

Prereg: `prereg/PREREG_K_ZA.md` (frozen and committed before fitting).
Primary line 3.5; target = stats-feed yellows (frozen target-source
decision in the prereg: the dev-era and virgin-era event feeds
publish no plain-yellow events, so no event-unified target exists in
either window). All numbers recomputed by the coordinator from the
per-match dev CSV against the league CSV (0 target mismatches).

## Dev (seed 2022/2023; scored 2023/2024–2024/2025, n = 447)

| Arm | Pooled LL@3.5 | 2023/2024 | 2024/2025 |
|---|---|---|---|
| Gate Zero | 0.7477 | 0.7622 | 0.7313 |
| League base rate | 0.7433 | — | — |
| Naive trailing-10 | 0.7189 | — | — |

## Gate arithmetic

Dev gate requires pooled LL@3.5 to beat BOTH baselines. Gate Zero
**loses to both**: the league base rate (0.7477 > 0.7433) and naive
trailing-10 (0.7477 > 0.7189). The production cards pattern is worse
than simply trailing each team's recent card counts in this league,
despite healthy trait reliabilities (yellows for 0.578 / against
0.608) — the naive component carries the signal and the ratings/NB
layer subtracts from it. Gate Zero fails its dev gate; the **virgin
was NOT read**.

**K-ZA FAILS. Nothing ships.** 2026/2027 remains the untouched
confirmatory window.
