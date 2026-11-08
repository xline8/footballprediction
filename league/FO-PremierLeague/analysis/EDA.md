# Phase 3 — EDA: Faroe Islands Premier League

EDA uses the 809 non-awarded matches. The awarded source row is excluded
from every rate below. 2026 is shown as a complete virgin season for level
inspection only; it is not used for fitting.

## Levels by season

| season | n | goals/m | home goals/m | HW | D | AW | OU2.5 | BTTS | YC/m | YC over3.5 | YC over4.5 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2021 | 135 | 3.630 | 1.911 | .459 | .170 | .370 | .696 | .519 | 3.778 | .541 | .341 |
| 2022 | 134 | 3.276 | 1.701 | .418 | .172 | .410 | .619 | .493 | 3.858 | .604 | .388 |
| 2023 | 135 | 3.148 | 1.719 | .474 | .156 | .370 | .600 | .481 | 4.141 | .630 | .385 |
| 2024 | 135 | 3.296 | 1.867 | .533 | .126 | .341 | .696 | .481 | 4.252 | .600 | .363 |
| 2025 | 135 | 3.630 | 1.807 | .400 | .200 | .400 | .719 | .593 | 3.844 | .541 | .415 |
| 2026 | 135 | 2.815 | 1.467 | .393 | .274 | .333 | .541 | .556 | 3.748 | .541 | .319 |

Pooled goals are 3.299 per match (3.30 rounded). First-half goals are
1,178 of 2,669 total, share **0.4414**. Unified yellows are Yellow plus YellowRed;
there are 1,107 first-half yellows out of the pooled unified-yellow total of
3,185, share **0.3476**. Per-season first-half goal shares are 0.443, 0.476, 0.466,
0.400, 0.420, and 0.447 (2021–2026); pooled first-half yellow shares range
from 0.326 to 0.394.

## Findings

**F1 — Levels drift, and 2026 is low-scoring.** Goals range from 2.815 in
2026 to 3.630 in 2021 and 2025. The 2026 OU2.5 rate is .541 versus .659 in
the 2022–2025 development window. The low 2026 level is recorded, not
adjusted away.

**F2 — Team traits are signal.** Odd-season (2021/2023/2025) versus
even-season (2022/2024/2026) team aggregates, Pearson r, ten teams with at
least 20 matches in each half: goals-for **0.876**, goals-against **0.928**,
yellows-for **0.869**, yellows-against **0.851**.

**F3 — Half shares support frozen constants.** Per-match first-half goal
share variance is 0.1005; binomial-noise expectation is 0.0994, leaving true
variance about 0.0011. Team-specific first-half shares are therefore not
used. Freeze presentation constants at goals **0.441** and unified yellows
**0.348**.

**F4 — Churn is real, but there is no mover source.** There are 13 team ids
over six seasons and typically two entrants/exits per season. The warehouse
has no 1. deild feeder tier, so no promoted-team tier offset can be measured.
The cup is not a substitute for a feeder tier.

**F5 — Cards are a viable target.** Unified yellows average 4.024 per match
in 2022–2025, variance 4.617, with P(over 2.5)=.744, P(over 3.5)=.594,
P(over 4.5)=.388. The 2026 virgin mean is 3.748 and P(over 3.5)=.541.

**F6 — Several tempting measurements do not exist.** There are no SOT,
corners, total shots, xG, or shotmap observations in any payload. Referee
text is empty in all 810 payloads. Stats and shotmap keys are not evidence
of coverage.

## Half and reliability summary

The machine-readable values are in `eda_summary.json`. The chart builder
uses those frozen values and the CSV; it does not read 2026 for fitting.
