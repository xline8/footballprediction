# Exploratory data analysis — Malaysia Liga Super

All fitted-window calculations use model rows only (`is_awarded=0`). Virgin and reserve values are inventory-level aggregates only.

## F1 — levels

| Season | n | Goals | Home | Away | HW | D | AW | OU1.5 | OU2.5 | OU3.5 | BTTS |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2021 | 132 | 2.7045 | 1.4394 | 1.2652 | .4091 | .2576 | .3333 | .7727 | .5303 | .2879 | .5227 |
| 2022 | 132 | 2.9394 | 1.7576 | 1.1818 | .4697 | .2045 | .3258 | .7803 | .5758 | .3561 | .5227 |
| 2023 | 182 | 3.4341 | 1.8187 | 1.6154 | .4780 | .1758 | .3462 | .8297 | .6209 | .4341 | .4890 |
| 2024/2025 | 155 | 3.0452 | 1.6323 | 1.4129 | .4065 | .2323 | .3613 | .8065 | .5613 | .3548 | .5032 |
| 2025/2026 virgin | 156 | 3.2949 | 1.7500 | 1.5449 | .3974 | .2372 | .3654 | .8077 | .6026 | .4103 | .4872 |
| 2026/2027 reserve | 35 | 3.5714 | 1.9714 | 1.6000 | .5429 | .1143 | .3429 | .8857 | .7429 | .4286 | .4857 |
| Dev pooled | 469 | 3.1663 | 1.7399 | 1.4264 | .4520 | .2026 | .3454 | .8081 | .5885 | .3859 | .5032 |

**F1 — levels and drift.** The dev window is high-scoring at 3.1663 goals per match, with a home-goal advantage of 0.3134. The partial 2026/2027 level is not comparable to a complete season.

## F2 — team traits

Chronological split-half reliability is GF r=.8381 and GA r=.7715 over 39 team-seasons in the scored 2022–2024/2025 window. The 2021–2024/2025 era gives GF r=.8269 and GA r=.7303 over 51 team-seasons. Across all complete model seasons through 2025/2026, GF r=.8494 and GA r=.7107 over 64 team-seasons.

**F2 verdict: SIGNAL.** A ratings architecture has persistent team signal.

## F3 — halves

The frozen presentation constant is `goals_1h_share = 1125/2481 = 0.4534`, from 759 eventful, non-awarded model matches. On the 756 matches with at least one goal, observed per-match share variance is 0.097829 versus binomial noise 0.105540; the ratio is 0.926946 and implied true variance is 0.000000.

**F3 verdict: NOISE.** Half shares are not a team covariate. The constant is presentation-only and may be used only after a goals arm passes.

## F4 — cards and dispersion

Card events are sparse: 127 total, 88 Red and 39 YellowRed, with no plain Yellow target. Match-total goals have dev pooled variance/mean 1.1199; the 2023 and 2025/2026 season ratios are 1.2683 and 1.3900, respectively. This supports retaining the standard goals likelihood while recording mild-to-moderate seasonal overdispersion descriptively.

SHRINK entrant expectations `(n_0, n_1_to_5, n_6_to_29, n_30_plus)` are `(2,0,10,0)` for 2022, `(4,0,2,8)` for 2023, and `(0,0,3,10)` for 2024/2025. The `n=1–5` bucket never occurs in dev, so SHRINK may be numerically identical to Gate Zero; that is measured, not a bug.
