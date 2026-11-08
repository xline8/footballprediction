# Model design — G-IS2

Phase A freezes one candidate: G-IS2, goals-only Dixon–Coles for 1X2, OU, BTTS and DC. The reference follows Besta's production pattern verbatim: 14 sweeps, damping 0.7, +0.25 smoothing, home-init 0.28, rho grid `(0.0, -0.05, -0.10, -0.15)` selected by weighted LL, MAXG 10, tau correction, 270-day decay half-life, and goals-only observations.

There are exactly three pre-registered arms: Gate Zero (unmodified), SHRINK (fitted attack/defence ratings multiplied by `min(1, target-season matches already played / 6)`), and X2 (SHRINK plus source-specific mover priors). For entrant source q, shift attack by `log((mu+dGF_q)/mu)` and defence by `log((mu+dGA_q)/mu)`, where mu is the decay-weighted training league mean and deltas use only completed prior transitions of q; fewer than three prior transitions means no source offset. First-time clubs stay at league-mean rating.

Validation is season-blocked walk-forward: dev 2022–2025, pooled n=528, seed 2021; virgin 2026, n=132, read once after dev. Baselines are expanding pre-target climatology. Primary line is OU2.5; metrics are 1X2 LL, RPS, and OU2.5 LL. Half lines are presentation only, splitting FT lambdas by frozen 0.4418. S/C/K/T are not candidates because their targets are absent.

Forbidden: half-share modelling, lineup/absence features, post-match snapshots, or any feature outside `FEATURES.md`.
