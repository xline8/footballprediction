# Model design — SLO-PrvaLiga

Scope is the whole regular phase: one single table, all rounds, no playoff or split-group exclusion. Awarded matches stay in the CSV but are excluded from every fit and score.

## Feasibility matrix

| Candidate | Status | Evidence |
|---|---|---|
| G-SLO goals | BUILD | 953 model rows; complete dev n=538 and virgin 2025/2026 n=161 |
| S-SLO SOT | NOT BUILDABLE | stats null and shotmap empty 956/956 |
| C-SLO corners | NOT BUILDABLE | stats null 956/956 |
| K-SLO cards/yellows | NOT BUILDABLE | plain Yellow events 0; referee named 0/956 |
| T-SLO total shots | NOT BUILDABLE | stats null and shotmap empty 956/956 |

## G-SLO reference architecture

Gate Zero is the production Dixon-Coles goals-only reference: direct Poisson log-likelihood maximisation with scipy L-BFGS, sum-to-zero attack/defence identification, ridge 1e-3, rho grid (0.0, -0.05, -0.10, -0.15), MAXG=10, standard DC tau correction, fitted home intercept initialized at 0.25, and frozen 270-day decay half-life. All observations are official goals; no xG blend is possible.

Arms are Gate Zero and SHRINK. SHRINK gives a team with n < 6 prior in-league matches a *= n/6 and d *= n/6, where n is counted strictly before the predicted season; n = 0 means exponents 0.0. NO ENTRANT is declared because no sibling Slovenia league exists; it adds no X2 offset.

Windows are warm-up 2021/2022 n=180, dev 2022/2023–2024/2025 n=538, virgin 2025/2026 n=161, and untouched reserve 2026/2027 n=74. Primary line is OU2.5. Baselines are pooled-training climatology and naive trailing-10 independent Poissons. Metrics are 1X2 log loss, RPS, and OU2.5 log loss.

On PASS only, halves are presentation via frozen `goals_1h_share=0.4498`. No halves model or feature is permitted.
