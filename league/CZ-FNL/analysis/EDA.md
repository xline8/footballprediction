# Exploratory Data Analysis

All figures below are generated from `eda_numbers.json` by `run_eda.py`.
The 2025/2026 and 2026/2027 rows are corpus description; they are not a
development gate read.

## Levels

| Season | n | Goals | Event Yellow | YellowRed | Red |
|---|---:|---:|---:|---:|---:|
| 2021/2022 | 240 | 2.712500 | 0.000000 | 0.108333 | 0.070833 |
| 2022/2023 | 240 | 2.775000 | 0.000000 | 0.079167 | 0.087500 |
| 2023/2024 | 240 | 2.862500 | 0.000000 | 0.108333 | 0.050000 |
| 2024/2025 | 240 | 2.520833 | 0.000000 | 0.054167 | 0.091667 |
| 2025/2026 | 240 | 2.679167 | 3.733333 | 0.070833 | 0.075000 |
| 2026/2027 | 111 | 3.018018 | 4.000000 | 0.036036 | 0.081081 |

SOT, corners, total shots, and possession are null in every season. The
plain-Yellow level flip is a feed change, not a stable dev target.

## Reliability and halves

Odd/even split-half reliability on 64 team-season units is available only for
goals: goals-for `r=0.327207`, goals-against `r=0.294798`. The dev era has
2,609 goals, of which 1,173 are first-half goals: the frozen goals constant is
`0.449598`.

The per-match first-half-share variance is `0.108868`; binomial noise at the
pooled share is `0.116160`, giving estimated true variance `-0.007292` (zero
within sampling error). Team split-half reliability of the share is
`r=0.130000` on 64 units — weak and consistent with zero within sampling
error, so it does not overturn the variance decomposition: per-team 1H
shares stay noise and only the league constant ships. Plain-Yellow halves are not computable in dev because the target
does not exist there; all other market half constants are null.

## Referees and movers

Referee coverage is 0 in each dev season and 2025/2026, then 49 in
2026/2027. Reliability is therefore not estimable, rather than zero by a
spurious calculation.

The X2 first-season deviations, computed from FNL plus the CZ-Liga index
(league 122, placement matches excluded), are:

| Boundary | Club | n | ΔGF | ΔGA |
|---|---|---:|---:|---:|
| →2022/2023 | Karvina | 30 | +0.545833 | −0.154167 |
| →2023/2024 | FC Zbrojovka Brno | 30 | −0.064583 | −0.031250 |
| →2024/2025 | FC Zlin | 30 | +0.239583 | −0.793750 |
| →2025/2026 | SK Dynamo České Budějovice | 30 | −0.306250 | +0.093750 |

The frozen cumulative offsets before target seasons are: 2022/2023 null;
2023/2024 `( +0.545833, −0.154167 )`; 2024/2025 `( +0.240625, −0.092708 )`;
2025/2026 `( +0.240278, −0.326389 )`. The Budějovice transition is the
honest reversal: attack is below mean and goals against above mean.

The dev pooled goals OU2.5 over-rate is `0.510417`. SOT, corners, total shots,
and cards primary lines are N/A: no valid target exists for a dev gate.
