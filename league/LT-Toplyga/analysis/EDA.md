# Exploratory data analysis — Lithuania Toplyga

`eda_compute.py` writes the JSON sources for this document and
`make_charts.py` writes the three charts. No model or arm is fitted; 2026 is
descriptive only.

## F1 — levels

| season | n | goals | home/away | H/D/A % | BTTS % | O1.5/O2.5/O3.5 % | home edge | var/mean |
|---|---:|---:|---:|---|---:|---|---:|---:|
| 2021 | 180 | 2.7389 | 1.4611/1.2778 | 40.00/27.22/32.78 | 53.89 | 81.67/50.00/28.33 | 0.1833 | 0.8337 |
| 2022 | 180 | 2.6167 | 1.4056/1.2111 | 41.67/25.56/32.78 | 45.00 | 74.44/50.00/26.67 | 0.1944 | 0.9619 |
| 2023 | 180 | 2.3944 | 1.2889/1.1056 | 41.11/25.56/33.33 | 38.33 | 68.33/40.56/23.89 | 0.1833 | 1.1642 |
| 2024 | 180 | 2.3500 | 1.1889/1.1611 | 36.67/27.78/35.56 | 43.33 | 63.33/44.44/25.00 | 0.0278 | 1.1338 |
| 2025 | 180 | 2.6611 | 1.4222/1.2389 | 40.00/24.44/35.56 | 51.11 | 74.44/52.22/28.89 | 0.1833 | 0.9370 |
| 2026 | 144 | 2.6458 | 1.4583/1.1875 | 40.97/27.78/31.25 | 52.08 | 75.00/53.47/28.47 | 0.2708 | 0.9963 |
| pooled | 1,044 | 2.5651 | 1.3678/1.1973 | 40.04/26.34/33.62 | 47.13 | 72.80/48.28/26.82 | 0.1705 | 1.0019 |

Verdict: **SIGNAL** for a goals rating architecture; levels drift enough to
justify the frozen time decay.

## F2 — trait reliability

Career chronological first-half versus second-half split-half correlation,
requiring ≥24 team matches: goals-for **r=0.7960, n=13 teams**; goals-against
**r=0.6918, n=13 teams**. Verdict: **SIGNAL**, a green light for goals
ratings.

## F3 — half shares

Pre-virgin event-derived matches: n=816, 1H share **0.430380**, observed
variance 0.116490, binomial floor 0.118132, residual **−0.001641**, ratio
0.986105. Verdict: **NOISE**. Freeze 0.43038 for presentation only. The 2026
descriptive share is 0.446194 over n=128 and is not fitted.

## F4 — movers and turnover

Per-season id IN/OUT: 2022 +2/−2, 2023 +1/−1, 2024 +1/−1, 2025 +1/−1,
2026 +1/−2; 2021 is the 10-id starting set. Pre-virgin arrival GF/GA/PPG
details are in `eda_numbers.json`. No Lithuanian sibling/1 Lyga data exists,
so X2 has no mover prior; new ids enter at league mean. Verdict: **NO X2
signal measurable**.

## F5 — thin-data note

Teams with fewer than six prior training matches at season start: 2022 **2**,
2023 **0**, 2024 **1**, 2025 **0**, 2026 **0**. This motivates SHRINK and is
not a tuning finding.

## Primary line and feasibility

Dev is 2022–2025, n=720: OU1.5 **0.7014**, OU2.5 **0.4681**, OU3.5 **0.2611**;
OU2.5 is closest to 0.5 and is frozen as primary. Goals is the only buildable
market. SOT/corners/shots have no stats feed; yellow cards do not exist;
xG/shotmap, referee, lineup and attendance targets are absent. No per-arm or
2026 arm numbers are computed.
