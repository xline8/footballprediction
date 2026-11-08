# Phase 3 — EDA: KR-KLeague3

All figures below use the regular-season population and come from
`analysis/eda_summary.json`. Percentages are shown as percentages; rates in
the source are proportions.

## Levels

| Season | n | goals | home goals | away goals | HW% | draw% | over 2.5% |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2021 | 202 | 2.307 | 1.223 | 1.084 | 38.1 | 31.7 | 39.1 |
| 2022 | 240 | 2.275 | 1.204 | 1.071 | 40.0 | 28.3 | 43.3 |
| 2023 | 210 | 2.343 | 1.267 | 1.076 | 40.0 | 29.0 | 43.8 |
| 2024 | 240 | 2.617 | 1.329 | 1.288 | 38.8 | 26.3 | 48.8 |
| 2025 | 210 | 2.400 | 1.224 | 1.176 | 40.5 | 21.0 | 48.1 |
| 2026* | 182 | 2.714 | 1.511 | 1.203 | 40.1 | 29.1 | 48.9 |
| pooled | 1,284 | 2.438 | 1.287 | 1.150 | 39.6 | 27.5 | 45.3 |

*2026 is in progress and reserved as confirmatory data. The pooled home
advantage is 39.6% home wins, with 1.287 home goals versus 1.150 away goals.
The goal variance/mean diagnostic is 2.6921 / 2.4377 = 1.104, a modestly
overdispersed pooled goal count.

The descriptive elevation is concentrated in 2024 and 2026: goals per match
are 2.617 and 2.714, compared with 2.275–2.400 in 2021–2023 and 2025. This
is a description, not a fitted adjustment.

For context, the K League 2 repository reports pooled goals of 2.58 and a
37.4% pooled home-win share in `league/KR-KLeague2/analysis/EDA.md`; K3 is
therefore lower-scoring (2.44) with a larger home-win share (39.6%). No J1
number is imported here.

## Trait reliability

The split-half test used 60 splits, seed 90210, and teams with at least 24
matches (n=23 teams). Goals-for reliability is r=0.441 and goals-against
reliability is r=0.739. No SOT, corners, shots, yellows, possession, box
touch, or referee trait can be tested because those source fields are absent.

## Halves and dispersion

From event times, the pooled first-half goal share is 0.4273. The season
shares are 0.4048, 0.4231, 0.4085, 0.4586, 0.4087, and 0.4451 for 2021–2026.
Observed variance is 0.1198 versus a binomial noise floor of 0.1230, giving
true variance -0.0031, approximately zero. A frozen 1H share of 0.4273 is
therefore justified for presentation only; it is not a team feature.

The event goal lists reconcile in 1,229/1,284 regular matches. The 55
failures are all early-2021 matches with empty goal-event lists, so the
half-time derivation is not extended to them. The card corpus has 57
YellowRed and 84 Red events and zero plain Yellow events; it is not a usable
plain-yellow target.

