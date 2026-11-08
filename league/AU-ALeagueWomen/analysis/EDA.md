# Exploratory data analysis

All levels below are regular-season rows. Development seasons are 2021/2022–2024/2025; 2025/2026 is shown only as the virgin design level.

| season | n | goals | total shots | SOT | corners | yellows |
|---|---:|---:|---:|---:|---:|---:|
| 2021/2022 | 70 | 3.31 | 27.16 | 10.61 | 9.49 | 2.36 |
| 2022/2023 | 99 | 3.05 | 28.31 | 10.81 | 9.59 | 2.55 |
| 2023/2024 | 132 | 3.07 | 27.70 | 11.39 | 9.05 | 2.37 |
| 2024/2025 | 138 | 3.03 | 27.46 | 10.29 | 9.05 | 1.97 |
| 2025/2026 virgin | 110 | 2.77 | 26.47 | 9.58 | 8.99 | 2.05 |

Across the 439 development regular matches, home/away goals are 1.69/1.36 (home edge +0.33); home win/draw/away win are 43.5%/24.8%/31.7%, Over 2.5 is 56.7% and BTTS is 59.9%. Development dispersion (variance/mean) is 1.07 goals, 1.32 SOT, 1.19 corners, 0.94 yellows and 1.35 total shots.

## Reliability and halves

Career-pooled development split-half reliability (12 teams meeting the 24-match rule; 60 odd/random splits) is: goals-for 0.575, total-shots-for 0.729, SOT-for 0.646, corners-for 0.569, yellow-for 0.546, box-touches-for 0.876, big-chance-for 0.662 and possession-for 0.923. Referee yellow strictness is 0.424 across 9 referees with at least 20 development assignments (416/439 usable non-empty referee identities). This passes the referee threshold for X8, with coverage carried explicitly. The payload-key coverage is 574/597, but 24 of those keyed rows have blank referee text; this is the one recomputation deviation from the coordinator facts.

For the requested season view, the following are exploratory odd/even split-half correlations by season (teams need at least 8 observations in that season; small-season values are not substituted for the pooled design statistic):

| season | goals | shots | SOT | corners | yellows | box touches | big chance | possession |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2021/2022 | .39 | .77 | .75 | .67 | .19 | .67 | .75 | .79 |
| 2022/2023 | .62 | .58 | .75 | .60 | .71 | .82 | .39 | .91 |
| 2023/2024 | .28 | .72 | .61 | .61 | .43 | .94 | .43 | .88 |
| 2024/2025 | .40 | .52 | .35 | .56 | .17 | .37 | .24 | .87 |

Using only regular matches with both period splits in 2023/2024–2024/2025 (268 usable rows), frozen 1H shares are goals 0.459, SOT 0.469, corners 0.480, total shots 0.467 and yellows 0.314. Excess observed share variance over the binomial sampling floor is +0.00283, +0.00124, +0.00385, +0.00225 and -0.00013 respectively: small/noise-scale, so constants are used and no team half-share feature is adopted.

At the development primary lines selected without virgin information, Over 2.5 goals is 56.7%, SOT Over 10.5 is 52.4%, corners Over 9.5 is 46.7%, cards Over 2.5 is 41.0%, and total shots Over 27.5 is 49.9%. (Coordinator correction before prereg commit: the draft labelled each count line one step too low for its computed rate — the rate is P(total >= line + 0.5) at the corrected line; each corrected line is the .5 line whose dev over-rate is closest to 0.5, verified independently on the 369-match evaluation window: SOT O10.5 52.8%, corners O9.5 46.3%, cards O2.5 40.9%, total shots O27.5 51.2%.)
