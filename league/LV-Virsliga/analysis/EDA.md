# Step 3 — EDA: LV-Virsliga

All computations in `analysis/eda_compute.py` → `eda_summary.json`.
Dev-era data only (seasons up to 2025); the virgin 2026 is never
read here. Count traits are measured on the stats era (2025)
because that is the only dev-era season where the targets exist.

## Levels

Goals per match by season: 2021 **3.018**, 2022 **2.978**, 2023
**2.906**, 2024 **3.078**, 2025 **2.967** — a stable, moderately
high-scoring league (J1 ~2.7, top-5 Europe ~2.8). Home goals
1.49–1.70 vs away 1.29–1.42 (home win rate 0.43–0.47). OU2.5
over-rate 0.50–0.64.

Stats-era count levels (2025, n=180): SOT **9.02**/match, corners
**9.98**, total shots **27.32** — all near the European
references (SOT ~9–10, corners ~10, shots ~25). Event-unified
yellows **4.79**/match — a normal-to-high card level. Home
possession mean 50.1%.

Primary lines (from the 2025 dev distribution, closest over-rate
to 0.5; scored-window over-rates agree): SOT **9.5** (0.444;
8.5 is 0.572), corners **9.5** (0.539), total shots **26.5**
(0.517), yellows **4.5** (0.522), goals OU **2.5**.

## Trait reliability (split-half by team, random halves)

| trait | window | n teams | r |
|---|---|---|---|
| goals for / against | dev seasons 2021–2025 | 13 | 0.946 / 0.942 |
| SOT for / against | 2025 | 10 | 0.887 / 0.882 |
| corners for / against | 2025 | 10 | 0.689 / 0.621 |
| total shots for / against | 2025 | 10 | 0.895 / 0.869 |
| yellows for / against | 2025 (events) | 10 | 0.598 / 0.582 |
| possession for | 2025 | 10 | 0.906 |
| fouls for | 2025 | 10 | 0.728 |
| big_chance for | 2025 | — | undefined (all zero) |

Team traits are genuinely reliable in this league — including
yellows (r≈0.6), far stronger than MA-BotolaPro's yellows-for
r=0.010. The count models start with real signal here.

## Halves (frozen constants, 2025 only)

| market | 1H share (2025) | n total | true per-match share var |
|---|---|---|---|
| goals | **0.4569** | 534 | 0.0 |
| SOT | **0.4637** | 1,624 | 0.0 |
| corners | **0.4816** | 1,796 | 0.0 |
| total shots | **0.4685** | 4,918 | 0.0 |
| yellow cards | **0.3306** | 862 | 0.0 |

Per-match 1H share variance is at or below binomial noise in
every market (observed var ≤ noise var), so the frozen-constant
treatment is correct for all five markets. Goals 1H share is
from goal-event times; SOT/corners/shots from period splits;
yellows from card-event times. Unlike MA-BotolaPro, LV has
period splits, so all five markets get FT + 1H/2H presentation.

## Entrants (mover evidence)

Entrant clubs (in the league after a season out; n=6 across
2022–2025: FK Tukums 2000, Auda, SK Super Nova in 2022; FK
Jelgava 2023; Grobiņa 2024; SK Super Nova again 2025) vs their
first season's league mean: ΔGF **−0.453**, ΔGA **+0.255** per
match — entrants score much less and concede more. This is a
large gap (vs MA's −0.107/+0.283) and motivates the sanctioned
SHRINK arm for goals. A J1-style X2 tier-offset arm cannot be
built: Latvia has exactly one league in the warehouse (Virsliga
226), so neighbour-tier membership is unobservable.

## Referee

2025: 40 matches with a referee, ~12 distinct referees after
merging diacritic variants, 1–5 matches each; yellows/match per
referee ranges 1.0–5.75 on those tiny samples. No referee rate
can be estimated, and 78% of matches have no referee at all.
X8 DROPPED.

## Reference points

Virsliga scores more than J1 (~2.97 vs ~2.7) with SOT/corners/
shots at European reference levels — a normal attacking league,
not a low-event one like Botola Pro. Trait reliabilities are
among the strongest in the program so far, which sets a high bar
for the dev gate: the baselines face the same strong traits.
