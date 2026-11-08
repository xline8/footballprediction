# Verdict — G-CN (goals): **FAIL**

Prereg: `prereg/PREREG_G_CN.md` (frozen and committed before fitting).
Era 2023+ only (2024 level break; 2021 COVID format and 2022 excluded).
Seed 2023; dev scored 2024+2025 (n = 480); virgin 2026.
All numbers recomputed by the coordinator from the per-match dev CSV
against the league CSV.

## Dev (season-blocked walk-forward; fit = era matches before season start)

| Arm | Pooled 1X2 LL | Pooled RPS | Pooled OU2.5 LL | 2024 LL | 2025 LL |
|---|---|---|---|---|---|
| Gate Zero | 0.9692 | 0.1948 | 0.6866 | 1.0063 | 0.9322 |
| SHRINK | 0.9692 | 0.1948 | 0.6866 | 1.0063 | 0.9322 |
| Climatology | 1.0625 | 0.2280 | 0.6802 | 1.0638 | 1.0612 |

SHRINK is numerically identical to Gate Zero: under season-blocked
fits a team's prior in-league count is either 0 (where SHRINK
coincides with the unseen-team rule) or ≥ 22 (factor 1). The same
degeneracy is visible in the RU/TH dev results; the arm was run and
reported per the prereg.

## Gate arithmetic

Dev gate requires pooled 1X2 LL AND RPS AND OU2.5 LL all to beat
climatology. Gate Zero wins 1X2 (0.9692 < 1.0625) and RPS
(0.1948 < 0.2280) but **loses the OU2.5 leg (0.6866 > 0.6802)** — the
DC's 1X2 discrimination is real, its total-goals level is not better
than the expanding base rate in a league whose scoring level stepped
up in 2024 (2.78 → 3.13 goals/match) and stayed high. Gate Zero fails
its dev gate; per the prereg, SHRINK is moot and the **virgin was NOT
read**.

**G-CN FAILS. Nothing ships.**
