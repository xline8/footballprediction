# Step 3 — EDA: GE-Erovnuli (goals only; other markets have no data)

## F1 — Levels by season (SIGNAL: per-league fit with decay justified)

| season | n | goals/match | home | away | HW | draw | OU2.5 | BTTS | 1H share |
|---|---|---|---|---|---|---|---|---|---|
| 2021 | 180 | 2.539 | 1.367 | 1.172 | .406 | .283 | .467 | .489 | .4311 |
| 2022 | 180 | 2.739 | 1.578 | 1.161 | .461 | .261 | .511 | .450 | .4604 |
| 2023 | 180 | 3.150 | 1.694 | 1.456 | .411 | .233 | .628 | .539 | .4497 |
| 2024 | 180 | 2.583 | 1.422 | 1.161 | .428 | .272 | .489 | .522 | .4645 |
| 2025 (virgin) | 180 | 2.694 | 1.433 | 1.261 | .400 | .233 | .506 | .528 | .4495 |
| 2026 (in progress) | 159 | 2.667 | 1.421 | 1.245 | .415 | .277 | .535 | .560 | .4764 |

Levels sit in the normal European band (2.54–3.15 gpm; 2023 is a high
outlier season). Home advantage is real but modest (home/away goal
ratio ≈ 1.20 pooled). Reference points: J1 ≈ 2.7 gpm with a stronger
home edge; GE is a touch lower-scoring with a weaker one.

## F2 — Team trait reliability, goals (SIGNAL)

Split-half (random halves of each team's dev-era matches, 2021–2024,
teams with ≥20 matches per half, n=13 teams): goals-for r = 0.817,
goals-against r = 0.963. Team attack/defence traits are real — a
scores-only Dixon-Coles fit has genuine signal. This is the entire
justification for building G-GE.

## F3 — Halves: frozen constant, presentation only

1H goal share by season: .431–.476 with no trend; pooled dev
(2021–2024) share = **0.4516**. Per the program's standing finding
(per-match half share ≈ noise around a league constant), halves are
NEVER fitted: FT lambdas are split by the frozen constant 0.4516 for
presentation only (1H λ = 0.4516·FT λ, 2H λ = 0.5484·FT λ). The
constant is frozen from dev seasons only — the virgin 2025 share
(.4495) was not used to set it.

## F4 — Movers (context for the SHRINK arm)

1–3 clubs enter per season from Erovnuli Liga 2 (no feeder data in
corpus). New clubs start at the league mean under Gate Zero and play
their first matches in season openers — exactly the G-J2 post-mortem
failure mode (extreme lambdas for 1–2-match teams). This motivates
the pre-registered SHRINK variant; it does not justify a cross-tier
offset (no feeder-tier scoring data exists to estimate one).

## F5 — Referee / cards / SOT / corners / shots: ABSENT

Coverage numbers in DATA_UNDERSTANDING (referee 0/1,059; stats null
1,059/1,059; shotmap empty 1,059/1,059; card events fragmentary).
No EDA is possible and none is faked.
