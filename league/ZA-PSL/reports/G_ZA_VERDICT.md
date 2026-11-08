# Verdict — G-ZA (goals): **FAIL**

Prereg: `prereg/PREREG_G_ZA.md` (frozen and committed before fitting).
All numbers below were recomputed by the coordinator from the per-match
dev CSV against the league CSV (0 target mismatches).

## Dev (season-blocked walk-forward; seed 2021/2022; scored 2022/2023–2024/2025, n = 690)

| Arm | 1X2 LL | RPS | OU2.5 LL |
|---|---|---|---|
| Gate Zero | 1.0230 | 0.2067 | 0.6476 |
| SHRINK | 1.0230 | 0.2067 | 0.6476 |
| Climatology | 1.0906 | 0.2268 | 0.6357 |

Per-season Gate Zero 1X2 LL: 1.0455 / 1.0262 / 0.9936 (climatology
1.0906 pooled; the model improves every season on 1X2).

## Gate arithmetic

Dev gate requires pooled 1X2 LL AND RPS to beat climatology AND OU2.5
LL to beat the base-rate baseline. Gate Zero beats climatology on 1X2
LL (1.0230 < 1.0906) and RPS (0.2067 < 0.2268) but **loses the OU2.5
leg: 0.6476 > 0.6357**. In a league scoring ≈2.0 goals/match with a
≈35% draw rate, the DC's 1X2 shape is genuinely informative while its
total-goals calibration at 2.5 is worse than the raw base rate. Gate
Zero therefore fails its own dev gate; per the prereg, variants are
moot and the **virgin was NOT read**.

SHRINK note (anticipated in the prereg, from the TH sibling run):
SHRINK's predictions are row-for-row identical to Gate Zero's. Under
season-blocked fitting a team's prior in-league match count is only
ever 0 (unseen ⇒ identical to Gate Zero) or ≥ 28 (a full season), so
the 1–5-match band the arm addresses never occurs in this league.

**G-ZA FAILS. Nothing ships.** 2026/2027 remains the untouched
confirmatory window.
