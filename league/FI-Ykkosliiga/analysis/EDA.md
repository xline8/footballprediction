# Step 3 — EDA: FI-Ykkosliiga

All figures below are from the fresh builder and `eda.py` run.  2026 is shown
only for inventory and season-level counts; it is not used for any fit or model
evaluation.

## Levels and home advantage

| Season | Goals | Home G | Away G | Home win | Over 2.5 |
|---|---:|---:|---:|---:|---:|
| 2021 | 2.809 | 1.506 | 1.302 | 0.426 | 0.525 |
| 2022 | 3.165 | 1.872 | 1.293 | 0.482 | 0.634 |
| 2023 | 2.915 | 1.646 | 1.268 | 0.463 | 0.537 |
| 2024 | 3.111 | 1.659 | 1.452 | 0.415 | 0.593 |
| 2025 | 3.281 | 1.741 | 1.541 | 0.430 | 0.637 |
| 2026 | 2.667 | 1.407 | 1.259 | 0.430 | 0.489 |

The dev seasons range from 2.809 to 3.281 goals/match. 2026 is the lowest
season at 2.667. This level swing is recorded before any modelling.

## Team-trait reliability

The split is chronological odd/even observations within each team, pooled over
2021–2025; a team contributes only with at least eight observations in each
half. Ratios are correlations of team-half means. Goals-for has 22 eligible
teams and r = 0.753; goals-against has 22 and r = 0.821. This supports the goals
trait. The event-yellow-for check has 22 eligible teams and r = -0.231, but the event feed is
structurally sparse in 2021–2025 and is not adopted as a model target.

## Frozen halves constant

For the dev inventory (2021–2025), 718 matches have at least one goal. The
pooled first-half goal share is **0.4462** over 2,315 goals. Per-match share
variance is 0.099739 versus 0.076641 expected from binomial noise, excess
0.023098. The season shares are 2021 0.4440 (n=152), 2022 0.4624 (n=159),
2023 0.4393 (n=152), 2024 0.4429 (n=125), and 2025 0.4402 (n=130). The share
is a reasonable presentation constant but not an input feature; all non-goal
half constants are null because stats are empty.

## Coverage

| Season | Events | Referee named | Card-event matches / coverage | Card events |
|---|---:|---:|---:|---:|
| 2021 | 153 | 0 | 27 / 16.7% | 32 |
| 2022 | 161 | 0 | 23 / 14.0% | 24 |
| 2023 | 154 | 0 | 19 / 11.6% | 21 |
| 2024 | 129 | 0 | 26 / 19.3% | 28 |
| 2025 | 131 | 0 | 22 / 16.3% | 26 |
| 2026 | 135 | 32 | 134 / 99.3% | 494 |

## Entrants

Across both league corpora, the Ykkösliiga team-set comparison identifies 18
entrants over 2022–2026: 7 were in Veikkausliiga the prior season and 11 were
not present in either corpus's prior season (tier-3/unknown origin). Pooling
all entrants is the preregistered X2 arm. Across these 18 first seasons, entrant
GF differs from the season's league team mean by **+0.0825** and GA by
**-0.0265**. The mixed-origin caveat is part of MODEL_DESIGN; this descriptive
result is not a reason to invent a post-hoc arm.

The raw cross-tier set check found Ykkösliiga entrants from Veikkausliiga:
FC KTP (2022), HIFK (2023), FC KTP (2024), EIF and FC Lahti (2025), FC KTP
and Haka (2026). The reverse set check found VPS (2022), FC KTP (2023), EIF
and IF Gnistan (2024), FC KTP and FF Jaro (2025), and FC Lahti and TPS (2026).
