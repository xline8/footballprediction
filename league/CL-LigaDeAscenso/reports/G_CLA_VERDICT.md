# Verdict — G-CLA (Chile Liga de Ascenso goals) — **FAIL (dev gate; virgin NOT read)**

Prereg: `prereg/PREREG_G_CLA.md` (frozen and committed before any
fitting). Population: finished + regular only (play-offs excluded;
62 fake-0-0 2021 placeholders excluded). Dev = season-blocked
walk-forward, seed 2021 (n = 178), scored 2022–2024 (n = 752).
All headline numbers below were recomputed independently by the
coordinator from `engine/goals/dev_predictions.csv` and the league
CSV and match the engine's `results_dev.json` to 4 decimals.

## Dev results (pooled, n = 752)

| Arm | 1X2 LL | RPS | OU2.5 LL |
|---|---|---|---|
| Climatology (baseline) | **1.0853** | **0.2293** | **0.6939** |
| Gate Zero | 1.1007 | 0.2351 | 0.7249 |
| SHRINK | 1.1007 | 0.2351 | 0.7249 |
| X2 mover | 1.1137 | 0.2385 | 0.7327 |

Per season (1X2 LL): Gate Zero 1.1039 / 1.0744 / 1.1235 vs
climatology 1.0792 / 1.0727 / 1.1049 (2022 / 2023 / 2024) — Gate
Zero loses to climatology in **every** dev season, on **every**
metric (RPS and OU2.5 LL included; see `results_dev.json`).

## Gate arithmetic (mechanical, per the frozen prereg)

- Dev gate: pooled dev 1X2 LL **and** RPS must beat climatology,
  and OU2.5 LL must beat the base-rate baseline. Gate Zero beats
  **none** of the three (1.1007 > 1.0853; 0.2351 > 0.2293;
  0.7249 > 0.6939). **Gate Zero fails its dev gate.**
- Consequence frozen in the prereg: variants are moot, the verdict
  is FAIL, and the virgin is **NOT read**. `results_virgin.json`
  records `virgin_read: false`. The 2025 virgin remains intact for
  a future, separately pre-registered build.
- Variant notes (recorded, not gated on): **SHRINK never bites** —
  0 of 2,256 dev predictions differ from Gate Zero, because under
  season-blocked fitting no team ever has 1–5 prior in-league
  matches at a season start (arrivals have exactly 0, where SHRINK
  coincides with Gate Zero's unseen rule; incumbents have ≥ 12).
  Same structural finding as the parent Primera build. **X2
  genuinely bites** (150 of 752 dev matches differ — the blended
  relegated teams and their opponents) and is worse than Gate Zero
  on all three dev metrics, so it would have failed the dev gate
  on its own as well.

## What ships

Nothing. No fitted params, no predictions CSV. The engine, dev
results and this verdict are the complete record. G-CLA = FAIL.
