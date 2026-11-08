# Step 6 — Model Design: IT-SerieC

## Feasibility matrix

| Candidate | Target exists? | Virgin window contains target? | Buildable |
|---|---|---|---|
| **G-ITC goals** | Yes — FT score in 6,184/6,184 finished matches | Yes — 2025/2026, 1,102 regular matches | **YES** |
| S-ITC SOT | No complete-season stats/shotmap | No | **NO — documented not-buildable** |
| C-ITC corners | No complete-season stats | No | **NO — documented not-buildable** |
| K-ITC cards | No complete-season stats/referee | No | **NO — documented not-buildable** |
| T-ITC total shots | No complete-season stats/shotmap | No | **NO — documented not-buildable** |

## Candidate G-ITC — goals model

The design mirrors the production Dixon-Coles reference: iterative
multiplicative fit, 14 sweeps, damping 0.7, +0.25 smoothing, fitted home
advantage, rho grid (0.0, -0.05, -0.10, -0.15) by weighted log-likelihood,
MAXG 10, and 270-day time-decay half-life. The observation is goals-only.

Arms are frozen as:

1. **Gate Zero** — unseen teams start at league mean.
2. **SHRINK** — Gate Zero plus rating scaling by n/6 for teams with fewer than
   six prior in-league matches. The F4 mover offset is not included.

Use season-blocked walk-forward evaluation: training seed **2021/2022**;
development evaluation **2022/2023 + 2023/2024 + 2024/2025**; virgin
**2025/2026 (complete, 1,102 regular-phase matches)**, read once only for arms
passing the dev gate. **2026/2027 is in-progress and reserved confirmatory,
not read.** The primary line is OU 2.5. Baselines are expanding prior-season
climatology for 1X2 and OU 2.5.

Gate legs are the identical preregistered goals gates: development versus
climatology on 1X2 log loss, RPS, and OU2.5 log loss; virgin (i) log loss no
worse than Gate Zero and climatology, (ii) calibration breach <=1pp clean
PASS, <=1 SE provisional PASS, otherwise FAIL, on home-win and OU2.5, and
(iii) per-season sign checks for variants. Both-pass rule; among passing arms,
lower virgin log loss ships, ties to the simpler arm. Presentation is FT-only.
