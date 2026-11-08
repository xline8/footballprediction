# Model design — Brazil Série C

There is one candidate: **G-BRC (goals)**. The reference is production Dixon–Coles (`model_v2.py`, class `DC`, hl=270) with the production blend-with-fallback; because xG is absent, the blend is goals-only in effect. No model is fitted in this build and no preregistration is written.

Arms (design only): (1) **Gate Zero**, the unmodified reference; (2) **SHRINK**, the sanctioned G-J2 lesson, multiplying ratings for teams with fewer than six prior in-league matches by n/6 toward the league mean at prediction time; (3) **X2**, two-sided cross-tier priors in lambda space for ex-B down-movers and newcomer up-movers. X2 offsets are estimated only from transitions into 2022–2025, never transition into virgin 2026. Pooled offsets are ex-B dGF −0.0405/dGA −0.0868 and newcomers dGF −0.0627/dGA +0.0667. X2 does not stack with SHRINK.

Dev is season-blocked walk-forward, seed 2021, scored 2022–2025, pooled n=856. The dev gate requires pooled 1X2 log loss and RPS to beat climatology and OU2.5 log loss to beat the base-rate baseline. A dead arm makes the virgin unread. Primary line is OU2.5.

Virgin is complete 2026, n=214 fit-set matches, read once and only for arms passing dev. Virgin legs are 1X2 LL ≤ Gate Zero and ≤ climatology; pooled home-win and OU2.5-over calibration absolute error ≤1.0 percentage point, with a breach within one SE recorded PROVISIONAL PASS and beyond one SE FAIL; and for variants, arm LL ≤ Gate Zero LL in at least half of dev seasons. If both pass, ship lower pooled virgin 1X2 LL; ties go Gate Zero, then SHRINK, then X2. S-BRC, C-BRC, K-BRC, and T-BRC are not candidates because their targets are absent in every season, including virgin 2026.

The 2026 complete season is the most recent complete season, so there is no confirmatory window. Final legs remain in the CSV but are excluded by the fit-set rule.
