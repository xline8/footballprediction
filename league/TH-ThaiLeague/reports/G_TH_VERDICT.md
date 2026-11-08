# Verdict — G-TH (goals): **FAIL**

Prereg: `prereg/PREREG_G_TH.md` (frozen and committed before fitting).
All numbers below were recomputed by the coordinator from the per-match
dev CSV against the league CSV (0 target mismatches).

## Dev (season-blocked walk-forward; seed 2021/2022; scored 2022/2023–2024/2025, n = 720)

| Arm | 1X2 LL | RPS | OU2.5 LL |
|---|---|---|---|
| Gate Zero | 0.9843 | 0.1979 | 0.7152 |
| SHRINK | 0.9843 | 0.1979 | 0.7152 |
| Climatology | 1.0526 | 0.2200 | 0.6921 |

Per-season Gate Zero 1X2 LL: 1.0135 / 0.9858 / 0.9536 (climatology
1.0507 / 1.0606 / ≈1.047).

## Gate arithmetic

Dev gate requires pooled 1X2 LL AND RPS to beat climatology AND OU2.5 LL
to beat the base-rate baseline. Gate Zero beats climatology on 1X2 LL
(0.9843 < 1.0526) and RPS (0.1979 < 0.2200) but **loses the OU2.5 leg:
0.7152 > 0.6921**. Gate Zero therefore fails its own dev gate; per the
prereg, variants are moot and the **virgin was NOT read**.

SHRINK note (recorded finding, anticipated in the prereg): SHRINK's
predictions are row-for-row identical to Gate Zero's. Under season-blocked
fitting a team's prior in-league match count is only ever 0 (unseen ⇒
identical to Gate Zero) or ≥ 30 (a full season), so the 1–5-match band
the arm addresses never occurs in this league.

**G-TH FAILS. Nothing ships.** 2026/2027 remains the untouched
confirmatory window.
