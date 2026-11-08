# Step 6 — Model Design (RO-LigaII)

No fitting, model code, preregistration or virgin read occurs in this build. The windows and candidate definitions below are the frozen design for the next step.

All candidates use training seed 2021/2022. Development is walk-forward and season-blocked over 2022/2023, 2023/2024 and 2024/2025, pooled n = 786 on the inclusion set. The virgin primary is 2025/2026, n = 317, complete, and is read once only for arms passing the dev gate. 2026/2027, n = 140 and in progress, is reserved confirmatory data and is not read here. Calibration is programme-wide: absolute breach <= 1.0 percentage point is clean PASS; <= 1 standard error is PROVISIONAL PASS; otherwise FAIL.

## G-RL2 — goals

Build the Dixon–Coles goals-only production pattern (`model_v2.py`, hl=270). Compare Gate Zero with the sanctioned SHRINK arm: at prediction time, ratings for teams with fewer than six prior in-league matches use `a *= n/6` and `d *= n/6`. Pre-state: because season-start prior counts are always 0 or at least 25, season-blocked fitting may make SHRINK numerically identical to Gate Zero; verify mechanically before interpreting it. Evaluate 1X2 log loss/RPS and OU2.5 log loss against climatology.

## Other candidate markets

- S-RL2 SOT: **NOT BUILDABLE**. No SOT source exists in any season.
- C-RL2 corners: **NOT BUILDABLE**. No corners source exists in any season.
- K-RL2 cards: **NOT BUILDABLE**. No stats feed and zero straight-Yellow events exist in all 1,513 files. Red/YellowRed events are audit-only rare-event counts.
- T-RL2 total shots: **NOT BUILDABLE**. No shots source exists in any season.

## Halves

If G-RL2 ships, reports may show FT plus 1H/2H using the frozen goals first-half constant 0.457419. This is presentation only and is not a team or match feature.
