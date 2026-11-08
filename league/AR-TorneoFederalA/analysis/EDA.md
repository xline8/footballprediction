# Exploratory data analysis

All descriptive calculations below use only 2021–2025. The 2026 group count is an inventory completeness condition, not an outcome sample.

## Levels

| season | n | goals/match | home goals | away goals | home win % | draw % |
|---|---:|---:|---:|---:|---:|---:|
| 2021 | 450 | 2.2133 | 1.3044 | 0.9089 | 47.778 | 30.889 |
| 2022 | 544 | 2.1250 | 1.3401 | 0.7849 | 50.000 | 28.860 |
| 2023 | 576 | 2.1285 | 1.3785 | 0.7500 | 54.340 | 25.868 |
| 2024 | 477 | 1.8889 | 1.1971 | 0.6918 | 49.057 | 31.027 |
| 2025 | 486 | 2.0761 | 1.3086 | 0.7675 | 49.588 | 27.984 |

Phase splits matter after the format change. In 2024, first/promotion/relegation goals per match are 1.8611 / 1.9306 / 1.9630. In 2025 they are 2.0679 / 1.9028 / 2.2444. Overall home-win rate is 50.336%; by phase it is 50.000% first, 58.333% promotion, and 47.953% relegation.

## Reliability and halves

The split-half team-season reliability correlations are 0.23564 for goals for and 0.42108 for goals against (177 team-seasons). These are useful as weak-to-moderate descriptive traits, supporting trailing goal means but not adding unsupported covariates.

For the 2,249 EDA matches with event-derived halves, the 1H goal share (ratio of sums) is 0.463826. Observed share variance is 0.13718731 against a binomial noise floor of 0.13896050; the variance is not above the frozen-constant threshold. Goals therefore get a frozen presentation constant only, not a team halves model.

## Primary lines and absent targets

Pooled over-rate is 60.876% for OU 1.5, 35.728% for OU 2.5, and 16.305% for OU 3.5. SOT, corners, cards (Yellow), total shots, xG, xGOT, and territory fields are absent because the payload counts are all zero. Referee coverage is 0%. The exact machine-readable inventory and EDA outputs are in `inventory_summary.json` and `eda_summary.json`.

## Movers (F4)

Using FotMob team ids and a same-warehouse cross-check against parent 8965, newcomer team-blocks in 2022–2025 number 23, with pooled GF/GA gaps of +0.05535 / +0.00444 goals per match versus their season team-match means. From Nacional: n=3 blocks, +0.1056 / −0.0001. From below or the cross-competition path: n=20 blocks, +0.0478 / +0.0051. These are the X2 preregistration inputs; they are not hard-coded Phase-A model constants.
