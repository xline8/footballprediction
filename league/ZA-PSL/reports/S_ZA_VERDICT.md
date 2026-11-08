# Verdict — S-ZA (shots on target): **FAIL**

Prereg: `prereg/PREREG_S_ZA.md` (frozen and committed before fitting).
Primary line 6.5. All numbers recomputed by the coordinator from the
per-match dev CSV against the league CSV (0 target mismatches).

## Dev (warm-up 2022/2023; scored 2023/2024–2024/2025, n = 448)

| Arm | Pooled LL@6.5 | 2023/2024 | 2024/2025 |
|---|---|---|---|
| Gate Zero (GZ) | 0.6946 | 0.6940 | 0.6953 |
| RS | 0.6946 | 0.6928 | 0.6967 |
| League base rate | 0.6944 | — | — |
| Naive trailing-10 | 0.7050 | — | — |

## Gate arithmetic

Dev gate requires pooled LL@6.5 to beat BOTH baselines. Gate Zero
beats naive trailing-10 (0.6946 < 0.7050) but **loses to the league
base rate by 0.0002 (0.6946 > 0.6944)** — the v5 pattern extracts no
usable signal beyond the prior-seasons over-rate in this league
(SOT-against reliability is only 0.340 here). Gate Zero fails its dev
gate; per the prereg, RS is moot (its pooled dev LL is identical to
four decimals anyway) and the **virgin was NOT read**.

**S-ZA FAILS. Nothing ships.** 2026/2027 remains the untouched
confirmatory window.
