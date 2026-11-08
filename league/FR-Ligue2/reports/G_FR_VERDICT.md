# Verdict — G-FR (FR-Ligue2 goals)

**FAIL at the dev gate. Virgin 2025/2026 deliberately NOT read.
Nothing ships.**

Calibration convention (league-wide): actual − predicted.
Dev = season-blocked walk-forward, seed 2021/2022, scored
2022/2023–2024/2025, pooled n = 1,065. Prereg: `prereg/PREREG_G_FR.md`.

## Dev gate (pooled)

| Arm | 1X2 LL | RPS | OU2.5 LL |
|---|---:|---:|---:|
| Gate Zero | 1.0867 | 0.2298 | 0.7104 |
| SHRINK | 1.0867 | 0.2298 | 0.7104 |
| X2 | 1.0848 | 0.2285 | 0.7081 |
| Climatology / base rate | **1.0747** | **0.2272** | **0.6927** |

Gate Zero loses **all three** dev legs to climatology (1X2 LL
1.0867 > 1.0747; RPS 0.2298 > 0.2272; OU2.5 LL 0.7104 > 0.6927).
Under the frozen rule the variants are moot and the virgin is not
read — recorded in `engine/goals/results_virgin.json`
(`virgin_read: false`).

Notes:
- SHRINK is numerically identical to Gate Zero in this league: with
  season-blocked fits, every team in a target season has either 0
  prior in-league matches (where SHRINK's rule equals Gate Zero's
  unseen rule by construction) or a full prior season (≥ 34 matches),
  so the 1–5-match band the arm targets never occurs.
- X2 fired as designed — mover counts per target season 5 / 6 / 5
  (Ligue 1: 3/4/3, Ligue 3: 2/2/2) — and improved on Gate Zero
  (1X2 LL −0.0019 pooled; it even beat climatology on 1X2 in
  2022/2023, 1.0677 vs 1.0755), but it still loses climatology
  pooled and loses the OU2.5 leg in every season (0.6893 / 0.7241 /
  0.7117 vs base 0.6869 / 0.6958 / 0.6960). The programme's usual
  binding constraint — the totals leg — binds here too.
- Coordinator verification: the dev harness was re-run independently;
  `results_dev.json` reproduced exactly.
