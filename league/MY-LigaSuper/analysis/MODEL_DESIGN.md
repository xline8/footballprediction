# Model design — Malaysia Liga Super

The scope is the regular single table. Awarded matches remain in the CSV but are excluded from every fit and score.

## Feasibility matrix

| Candidate | Status | Evidence |
|---|---|---|
| G-MY goals | BUILD | 792 model rows; complete dev n=469 and virgin 2025/2026 n=156 |
| S-MY SOT | NOT BUILDABLE | stats null and shotmap empty 793/793 |
| C-MY corners | NOT BUILDABLE | stats null 793/793 |
| K-MY cards/yellows | NOT BUILDABLE | plain Yellow events 0; referee named 0/793 |
| T-MY total shots | NOT BUILDABLE | stats null and shotmap empty 793/793 |

## G-MY reference architecture

The reference is the production Dixon-Coles pattern: direct Poisson log-likelihood maximisation with scipy L-BFGS, sum-to-zero attack/defence identification, ridge 1e-3, rho grid `(0.0, -0.05, -0.10, -0.15)`, MAXG=10, standard Dixon-Coles tau correction, fitted home intercept initialized at 0.25, and frozen 270-day decay. Observations are official goals only. Fit scope is all model matches strictly before the target season's first match date.

Arms are Gate Zero and SHRINK. Gate Zero gives entrants league-mean expectations. SHRINK, at prediction time, multiplies attack and defence exponents by `n/6` when a team has fewer than six prior in-league matches; `n` is counted strictly before the predicted season and `n=0` uses the league-mean fallback. There is no X2 mover arm.

Halves are presentation-only through the frozen `goals_1h_share=0.4534`, on PASS only. No halves mechanism enters the fit.
