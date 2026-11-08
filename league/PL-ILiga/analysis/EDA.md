# Phase 3 — EDA: Poland I Liga

All numeric values below are emitted by eda_compute.py in eda_numbers.json.

## Levels

Across complete seasons, regular-only pooled levels are 2.695 goals, 1.451 home goals, and 1.244 away goals per match. Home/draw/away outcomes are 40.0% / 27.8% / 32.2%. The dev-period OU2.5 over-rate is 0.497; scored seasons are 2022/2023, 2023/2024, and 2024/2025 with 918 regular matches. The virgin has 306 regular matches and the confirmatory season has 126.

## Reliability and halves

Goals-for split-half reliability is 0.721 and goals-against is 0.281, from 60 career-pooled random-half repetitions with seed 42 and 38 eligible team ids.

On 1,417 regular complete-season matches with events, the goals first-half share is 0.457 by ratio of sums. Observed variance is 0.1121, estimated true variance is -0.0033, and true SD is 0.0. This supports a frozen goals 1H presentation constant, not a team feature. No missing-feed reliability number is emitted.

## Newcomers and direction

Same-league newcomer pooling contains 30 newcomer team-seasons. Newcomers average 1.407 GF and 1.398 GA against league team means of 1.348 GF and 1.348 GA: gaps are +0.059 GF and +0.05 GA. The direction split is not stable enough for X2: pooled movers from Ekstraklasa are 1.493 GF and 1.316 GA, gaps +0.145 and -0.032; pooled movers from II Liga are 1.32 GF and 1.479 GA, gaps -0.028 and +0.131. The per-transition direction values are in eda_numbers.json.

## Card-event descriptives

These are descriptive only, never a target. Per season, Red / YellowRed totals and mean Reds per match among event-covered matches are: 2021/2022 25 / 40 / 0.227; 2022/2023 27 / 43 / 0.239; 2023/2024 38 / 46 / 0.291; 2024/2025 44 / 24 / 0.234; 2025/2026 49 / 1 / 0.168; 2026/2027 19 / 2 / 0.172.

## J1 X1–X9 checklist

X1 is SIGNAL for goals-only modelling: goals are complete, while xG is absent in all seasons. X2 is NOISE/UNSTABLE: the direction gaps above change sign across transitions. X3 set-play xG, X4 xG per shot, X5 target-rate feeds, X6 xGOT, X7 territory, X8 referee, and X9 possession/big chances are ABSENT because the required stats, shotmap, or referee feeds are absent. Referee data itself is 0.0% covered.

## Reproducibility

Run the builder, then eda_compute.py, then make_charts.py.

