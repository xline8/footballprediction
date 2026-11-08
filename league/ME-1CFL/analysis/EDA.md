# Exploratory data analysis — Montenegro 1. CFL

`eda_compute.py` writes the JSON sources for this document and
`make_charts.py` writes the three charts. No model or arm is fitted;
2025/2026 (virgin) and 2026/2027 (confirmatory, in progress) are
descriptive only. All numbers below come from `eda_numbers.json`.

## F1 — levels

| season | n | goals | home/away | H/D/A % | BTTS % | O1.5/O2.5/O3.5 % | home edge | var/mean |
|---|---:|---:|---:|---|---:|---|---:|---:|
| 2021/2022 | 179 | 2.6425 | 1.4413/1.2011 | 41.34/25.70/32.96 | 52.51 | 74.30/49.72/25.70 | 0.2402 | 1.0186 |
| 2022/2023 | 180 | 2.4778 | 1.3611/1.1167 | 40.56/30.00/29.44 | 50.56 | 68.33/48.89/23.89 | 0.2444 | 1.1519 |
| 2023/2024 | 180 | 2.4611 | 1.3500/1.1111 | 40.56/30.56/28.89 | 52.22 | 70.00/43.33/26.11 | 0.2389 | 1.0413 |
| 2024/2025 | 179 | 2.4581 | 1.3017/1.1564 | 39.11/26.82/34.08 | 48.60 | 72.07/41.34/22.35 | 0.1453 | 0.9700 |
| 2025/2026 | 180 | 2.3722 | 1.3778/0.9944 | 45.00/25.00/30.00 | 47.22 | 66.67/42.78/21.67 | 0.3833 | 1.1117 |
| 2026/2027 (partial) | 73 | 2.2603 | 1.2877/0.9726 | 38.36/31.51/30.14 | 38.36 | 60.27/39.73/21.92 | 0.3151 | 1.4751 |
| pooled | 971 | 2.4655 | 1.3605/1.1050 | 41.09/27.91/31.00 | 49.33 | 69.52/44.80/23.79 | 0.2554 | 1.0853 |
| pooled dev (22/23–24/25) | 539 | 2.4657 | 1.3377/1.1280 | 40.07/29.13/30.80 | 50.46 | 70.13/44.53/24.12 | 0.2096 | — |

Verdict: **SIGNAL** for a goals rating architecture, with two
cautions. First, levels drift: goals per match fall steadily from
2.64 (2021/2022) to 2.37 (2025/2026) and 2.26 in the partial
2026/2027 — that drift is what the frozen 270-day decay is for.
Second, the home edge is unstable by season (0.15 in 2024/2025,
0.38 in 2025/2026, pooled 0.26): the DC fit estimates home
advantage per window rather than assuming the pooled value.
Goal dispersion (variance/mean ≈ 1.09 pooled) is near-Poisson,
so the Poisson-DC family is not fighting the data.

Reference points: LT-Toplyga pooled 2.57 goals/match; J1 ≈ 2.6.
ME-1CFL at 2.47 is a slightly lower-scoring league, and its dev
OU2.5 over-rate (0.4453) sits further from 0.5 than LT's (0.4681)
— the base rate will be a harder totals baseline to beat.

## F2 — trait reliability

Standard program check (career chronological first-half versus
second-half split-half, teams with ≥24 matches, n=15 teams):
goals-for **r=0.1279**; goals-against **r=0.3759**. That is far
below LT-Toplyga (0.7960 / 0.6918) and J1 (0.69 / 0.62) on the
same check — and it is NOT a data error. The per-team halves show
why: attack strength drifts hard within careers. Mornar goes
0.91 → 1.35 GF, Sutjeska 1.75 → 1.38, Decic 1.39 → 1.16,
Otrant 0.76 → 2.04, Iskra 1.33 → 0.92; only Jezero (1.06 → 1.07)
and Petrovac (1.30 → 1.26) are flat. The chronological split
punishes exactly that drift.

Cross-check (season-parity split: odd vs even season start-years,
teams with ≥12 matches per side, n=12 teams): goals-for
**r=0.6902**; goals-against **r=0.6933**. Interleaving eras removes
the drift penalty and the between-team traits show up at the same
magnitude as LT/J1. Both numbers are in `eda_numbers.json`
(`reliability` and `reliability_parity`).

Verdict: **SIGNAL-CANDIDATE (mixed)**. Team traits exist
(parity r≈0.69 both sides), but attack strength is not stable
across eras (chronological GF r=0.13). This is precisely the
regime the reference architecture's 270-day decay is designed
for — recent matches weigh more because old ratings go stale —
and it is why F2 alone cannot pass the candidate: the dev
walk-forward gate is the arbiter. A goals model that ignored
decay (or pooled all history equally) would be mis-specified
here; the frozen reference does not.

## F3 — half shares

Pre-virgin event-derived matches (2021/2022–2024/2025, HT known):
n=815, 1H share **0.426643**, observed variance 0.117898,
binomial noise expectation 0.122492, residual **−0.004594**,
noise ratio 0.962. Verdict: **NOISE**. Freeze 0.426643 for
presentation only. The virgin season's descriptive share is
0.388759 over n=162 — lower, but descriptive only and not fitted;
the frozen constant does not move. (For reference: LT froze
0.43038, J1 0.412.)

## F4 — movers and turnover

Per-season id IN/OUT: 2022/2023 +2/−2 (FK Arsenal Tivat, Jedinstvo
BP in; Zeta, FK Podgorica out), 2023/2024 +1/−1 (OFK Mladost Donja
Gorica in; FK Iskra out), 2024/2025 +2/−2 (Otrant, FK Bokelj in;
Mladost, Rudar Pljevlja out), 2025/2026 +1/−1 (Mladost back in;
Otrant out), 2026/2027 +1/−1 (Otrant back in; Jedinstvo out).
2021/2022 is the 10-id starting set. Arrival GF/GA/PPG details
are in `eda_numbers.json` (`arrival_metrics`): new ids arrive at
0.86–1.19 GF and 1.08–1.64 GA per match vs league ≈1.23 GF —
i.e. new sides arrive slightly below average, as expected, but
with only 5 arrivals in the dev window and no cross-tier data,
no mover prior can be estimated. No Montenegrin sibling league
exists in the warehouse (only league id 232 under country
Montenegro), so X2 has no measurable prior. Verdict: **NO X2
signal measurable**.

Note the returning-id pattern: Mladost (out 2024/2025, back
2025/2026) and Otrant (out 2025/2026, back 2026/2027) re-enter
with 36 prior matches in the training window, so they are NOT
thin-data teams on return — only genuinely new ids start at zero
history.

## F5 — thin-data note

Teams with fewer than six prior training matches at season start:
2022/2023 **2** (the two new ids), 2023/2024 **1**, 2024/2025
**2**, 2025/2026 **0**, 2026/2027 **0**. This motivates SHRINK
and is not a tuning finding. As in LT-Toplyga, the thin teams are
brand-new ids with 0 training matches, whose SHRINK factor is 0
and whose Gate Zero prior is already a = d = 0 — so SHRINK is
expected to coincide with Gate Zero; it is run anyway and gated
like any arm.

## Primary line and feasibility

Dev is 2022/2023–2024/2025, n=539: OU1.5 **0.7013**, OU2.5
**0.4453**, OU3.5 **0.2412**; OU2.5 is closest to 0.5 and is frozen
as primary. Goals is the only buildable market. SOT/corners/total
shots have no stats feed and no shotmap shots (0/971 rows);
yellow cards do not exist (0 Yellow events in 971 matches);
xG, referee, lineup and attendance targets are absent. No
per-arm or virgin arm numbers are computed.
