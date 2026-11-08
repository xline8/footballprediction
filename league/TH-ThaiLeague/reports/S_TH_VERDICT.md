# Verdict — S-TH (shots on target): **FAIL**

Prereg: `prereg/PREREG_S_TH.md` (frozen and committed before fitting).
Primary line 9.5. All numbers recomputed by the coordinator from the
per-match dev CSV against the league CSV (0 target mismatches).

## Dev (per-match walk-forward; warm-up 2022/2023; scored 2023/2024–2024/2025, n = 480)

| Arm | Pooled LL@9.5 | 2023/2024 | 2024/2025 |
|---|---|---|---|
| Gate Zero | 0.6760 | 0.6777 | 0.6743 |
| RS | 0.6765 | 0.6766 | 0.6763 |
| League base rate | 0.7097 | — | — |
| Naive trailing-10 | 0.6717 | — | — |

## Gate arithmetic

Dev gate requires pooled LL@9.5 to beat BOTH baselines. Gate Zero beats
the league base rate (0.6760 < 0.7097) but **loses to naive trailing-10
(0.6760 > 0.6717)**. RS is worse still (0.6765). Gate Zero fails its dev
gate; per the prereg, variants are moot and the **virgin was NOT read**.

**S-TH FAILS. Nothing ships.**
