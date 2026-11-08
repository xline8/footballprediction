# Model design — MK-PrvaLiga

Scope is the whole regular phase: one single table, all rounds, no playoff or split-group exclusion. Awarded matches stay in the CSV but are excluded from every fit and score.

## Feasibility matrix

| Candidate | Status | Evidence |
|---|---|---|
| G-MK goals | BUILD | 1,009 model rows; complete dev n=549 and complete virgin 2025/2026 n=197 |
| S-MK SOT | NOT BUILDABLE | stats null and shotmap empty in 1,022/1,022 |
| C-MK corners | NOT BUILDABLE | stats null in 1,022/1,022 |
| K-MK cards/yellows | NOT BUILDABLE | plain Yellow events 0; referee named 0/1,022 |
| T-MK total shots | NOT BUILDABLE | stats null and shotmap empty in 1,022/1,022 |

## G-MK reference architecture

Gate Zero is the production Dixon-Coles goals-only reference: direct Poisson log-likelihood maximisation with scipy L-BFGS, sum-to-zero attack/defence identification, ridge 1e-3, rho grid (0.0, -0.05, -0.10, -0.15), MAXG=10, standard tau DC correction, fitted home intercept initialized at 0.25, and frozen decay half-life 270 days. All observations are official goals; no xG blend is possible.

Arms are Gate Zero and SHRINK. SHRINK is defined as follows: at prediction time a team with n < 6 prior in-league matches has a *= n/6 and d *= n/6, where n is matches played in the training data strictly before the predicted season; n >= 6 means no change; n = 0 means exponents 0.0. NO ENTRANT is declared as the no-mover arm because no sibling MK league exists; it adds no estimated X2 offset.

Windows are warm-up 2021/2022, dev 2022/2023–2024/2025 pooled n=549, virgin 2025/2026 n=197, and untouched reserve 2026/2027 n=65. Primary line is OU2.5. Baselines are pooled training climatology and naive trailing-10 independent Poissons. Metrics are 1X2 log loss, RPS, and OU2.5 log loss.

On PASS only, halves are presentation via frozen goals_1h_share=0.4323. No halves model or feature is permitted.
