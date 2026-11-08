# Exploratory data analysis

All results are descriptive. No model was fitted and no dev or
virgin harness was run. Computed by
`analysis/compute_eda.py` from `data/hn_matches.csv`; full numbers
in `analysis/eda_summary.json`. Levels are on regular-phase matches
unless stated; playoff levels are tabulated separately at the end.

## 1. Levels per season (regular phase)

| season | n | home goals | away goals | total goals | home/draw/away | OU2.5 | BTTS | dismissal events/match |
|---|---:|---:|---:|---:|---|---:|---:|---:|
| 2021/2022 - Apertura | 90 | 1.61 | 1.22 | 2.83 | 47.8% / 23.3% / 28.9% | 56.7% | 55.6% | 0.36 |
| 2021/2022 - Clausura | 90 | 1.60 | 1.13 | 2.73 | 51.1% / 16.7% / 32.2% | 55.6% | 46.7% | 0.30 |
| 2022/2023 - Apertura | 90 | 1.67 | 1.20 | 2.87 | 44.4% / 26.7% / 28.9% | 57.8% | 54.4% | 0.36 |
| 2022/2023 - Clausura | 90 | 1.54 | 1.10 | 2.64 | 44.4% / 32.2% / 23.3% | 47.8% | 56.7% | 0.29 |
| 2023/2024 - Apertura | 90 | 1.64 | 1.18 | 2.82 | 48.9% / 24.4% / 26.7% | 54.4% | 54.4% | 0.33 |
| 2023/2024 - Clausura | 90 | 1.49 | 0.91 | 2.40 | 51.1% / 24.4% / 24.4% | 45.6% | 45.6% | 0.38 |
| 2024/2025 - Apertura | 90 | 1.58 | 1.14 | 2.72 | 43.3% / 30.0% / 26.7% | 53.3% | 48.9% | 0.30 |
| 2024/2025 - Clausura | 90 | 1.36 | 1.00 | 2.36 | 38.9% / 37.8% / 23.3% | 36.7% | 51.1% | 0.41 |
| 2025/2026 - Apertura | 110 | 1.66 | 1.51 | 3.17 | 44.5% / 28.2% / 27.3% | 59.1% | 59.1% | 0.25 |
| 2025/2026 - Clausura | 110 | 1.45 | 1.22 | 2.67 | 42.7% / 29.1% / 28.2% | 49.1% | 58.2% | 0.39 |
| 2026/2027 - Apertura | 84 | 1.62 | 1.11 | 2.73 | 50.0% / 26.2% / 23.8% | 48.8% | 51.2% | 0.29 |
| **Pooled regular** | **1,024** | **1.56** | **1.17** | **2.73** | **46.0% / 27.2% / 26.8%** | **51.5%** | **53.1%** | **0.33** |

Reference points: the pooled 2.73 goals/match sits above the
J1 2021–2025 range (≈2.5) and above Guatemala's 2.31–2.47; the
home-win rate (46.0%) is below Guatemala's 49–60% and below the
top-5 norm (≈45–46% — in line). The 2025/2026 Apertura is the
goal-heaviest phase in the corpus (3.17/match, OU2.5 59.1%) and
the 2024/2025 Clausura the lightest (2.36/match, OU2.5 36.7%) —
a 0.81 goals/match swing between adjacent phases, i.e. phase
levels move around noticeably and a pooled climatology will be a
blunt baseline. No monotonic trend across seasons: levels oscillate
phase to phase rather than drifting.

Home advantage: home teams score 1.56 vs 1.17 away (ratio 1.33),
win 46.0% vs 26.8% away. The draw rate (27.2%) is high by top-5
standards — draws are the second-most-common outcome, which is
what makes the 1X2 log-loss gate hard (cf. GT's dev failure).

Playoff levels (descriptive only, never fitted): 108 matches,
2.40 goals/match pooled, home win 41.7% — lower-scoring and less
home-tilted than the regular phase, consistent with knockout
football being different football (the reason playoffs are
excluded from every fit and score).

## 2. Team traits — are goal rates reliable?

Career-pooled chronological split-half, using ratio-of-sums
team-match rates (each team's regular-phase matches split at the
chronological midpoint; minimum 6 matches per half):

- goals-for **r = 0.839** (n = 16 teams) — very strong. Attack
  strength is a stable team property in this league.
- goals-against **r = 0.320** (n = 16 teams) — moderate. Defence
  is real but much noisier than attack.

For comparison: Guatemala goals-for r = 0.410, goals-against
r = 0.730 — Honduras is the mirror image (attack reliable,
defence weak). El Salvador: attack r = 0.37, defence r = 0.36.
The DC ratings therefore have signal to work with on the attack
side; the gate, not optimism, decides whether that signal beats
climatology out of sample. No other trait can be tested: SOT,
corners, shots, cards and xG do not exist in the corpus.

## 3. Halves — the frozen-constant question

HT goals are event-derived for 1,079/1,132 matches (95.3%;
52 event-less matches + 1 awarded match with blanked HT are not
recoverable). Over recoverable matches: 1,394 first-half goals
out of 3,049 total, pooled 1H share **0.4572**.

Variance decomposition (the J1-audit method) on the 1,050
recoverable matches with ≥1 goal:

- observed variance of the per-match 1H share: **0.1163**
- expected sampling variance under a constant share
  (mean of p(1−p)/G_i): **0.1161**
- excess (true) variance: **0.0002** — true SD ≈ **1.4pp**,
  far inside the noise threshold of the variance estimate (0.0072)

Conclusion: the true per-match 1H-share variance is ≈ 0. The
1H share is a league constant with binomial sampling noise on
top, not a per-match or per-team quantity. **The goals 1H
constant is FROZEN at 0.4572** (1H λ = 0.4572 × FT λ,
2H λ = 0.5428 × FT λ), presentation only, never fitted. This
matches the top-5 (0.4419/0.4440), J1 (0.412) and SV (0.4335)
practice; GT's non-freeze rested on the raw variance alone
without this decomposition. No other market has a halves
constant (no SOT/corners/shots/cards data exist).

## 4. Format change (2025/26 expansion)

2021/22–2024/25: 10 teams, 18-round single round-robin + 10
playoff matches per phase. 2025/26: 11 teams (CD Choloma joins
the regular phase as the 11th club), 22-round double round-robin
(110 regular) + 12 semifinal-group matches + 2-legged final.
2026/27: 12 teams, single round-robin in progress (84 matches to
2026-11-09). One new club enters per expansion year; there is no
relegation/promotion churn inside the corpus beyond the
expansions (the same 10 core clubs appear in every phase).
Team turnover is therefore thin-data at the season edges — the
SHRINK arm exists for exactly that.

## 5. Cards (descriptive only)

365 dismissal events (253 Red + 112 YellowRed) in 1,132 matches
(0.32/match; 0.33/match on the regular phase). There are 0 plain
Yellow events, so no yellow-card target exists and no card rate
can be validated against a stats feed. Dismissals are not a
candidate target and not a feature.

## 6. Awarded matches

`3796146`, `3796174` (2021/2022 - Clausura, both official 3–0),
`5066531` (2025/2026 - Apertura, official 0–0). FT scores are
kept as official; HT is blanked (PREPROCESSING.md). They are 3
of 1,132 rows (0.3%) and do not move any level materially.

Charts are generated from `eda_summary.json` by `make_charts.py`.
