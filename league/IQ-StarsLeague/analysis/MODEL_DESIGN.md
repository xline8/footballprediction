# Step 6 — Model design: IQ-StarsLeague

## Feasibility

There is one candidate: **G-IQSL**, full-time goals with 1X2, OU, BTTS, and Dixon–Coles probabilities. S-IQSL, C-IQSL, T-IQSL, and K-IQSL are NOT BUILDABLE: stats is null in 2,032/2,032 payloads, shotmap shots are empty in 2,032/2,032, and events carry only Red/YellowRed card events with zero Yellow events in every season. No SOT, corners, total-shots, or yellow-card target exists in either dev or virgin payloads.

## G-IQSL

Reference: production goals-only Dixon–Coles (`model_v2.py` pattern), half-life 270 days, rho grid `0, -0.05, -0.10, -0.15`, and tau correction. No xG blend and no X2 prior.

Pre-registered arms (maximum two): **Gate Zero**, the unmodified reference with unseen teams starting at league mean; and **SHRINK**, Gate Zero plus attack/defence log-ratings for a team with fewer than six prior in-league matches scaled by `n/6` toward league mean. This is the pre-registered promoted-team opener answer from the G-J2 post-mortem.

Dev is season-blocked walk-forward: seed 2021/2022, score 2022/2023–2024/2025, fitting on all earlier regular matches. Virgin primary is 2025/2026 (379 complete played rows), read once only after the dev gate. 2026/2027 (130 rows, in progress) is confirmatory and is not part of this verdict; it is re-read at season end.

Primary line: OU 2.5, using the pooled dev over-rate (0.399 across the
three scored dev seasons, 440/1,104). Team goal traits are reliable at
career scale (EDA F2, split-half r ≈ 0.77), which supports the DC
ratings as architectural fitted state. Baselines are prior-season
climatology for 1X2 and OU2.5, plus naive trailing-10 where the template
requires it.

## GATE LEGS (frozen)

Dev: pooled dev 1X2 log loss and RPS must beat climatology, and OU2.5 log loss must beat the base-rate baseline. Gate Zero failing dev means G-IQSL FAILS, variants are moot, and virgin is not read.

Virgin: (i) 1X2 LL is ≤ Gate Zero and ≤ climatology; (ii) pooled home-win-rate and OU2.5-over-rate calibration each has `|breach| ≤ 1.0pp`, with breach defined as mean predicted rate − actual rate (pp), and a breach within 1 SE of the boundary is PROVISIONAL PASS, otherwise FAIL; (iii) the variant has a per-season dev sign check, LL no worse than Gate Zero in at least half of dev seasons. If both arms pass, ship lower pooled virgin 1X2 LL; ties go to Gate Zero. If one passes, ship it. None passes means FAIL and nothing ships.
