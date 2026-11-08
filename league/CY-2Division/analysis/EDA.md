# Exploratory data analysis — Cyprus 2. Division

`eda_compute.py` writes `eda_numbers.json` and
`inventory_summary.json`; `make_charts.py` writes the three required
charts. Pooled levels, per-season levels, home advantage, split-half
reliabilities, half-share noise tests, phase counts, team-id
stability, and the mover gap are in the JSON outputs.

Dev scored window: 2022/2023–2024/2025 (n = 682). Seed season
2021/2022. Virgin 2025/2026 (n = 232); confirmatory 2026/2027
(n = 56, partial). The only primary line is OU2.5 (dev over-rate
0.491, closest to 0.5 of 1.5 / 2.5 / 3.5).

## Levels

| Quantity (per match) | Pooled | Dev window |
|---|---|---|
| Goals | 2.59 | 2.62 |
| Home goals / away goals | 1.36 / 1.23 | — |
| Home win / draw / away win % | 40.9 / 22.8 / 36.3 | 43.4 / 20.8 / 35.8 |
| BTTS % / Over 2.5 % | 46.6 / — | — / 49.1 |
| Home advantage (goals) | +0.13 | +0.19 |

Goals by season: 2.39, 2.53, 2.56, 2.77, 2.71 (virgin), 2.46
(confirmatory, partial). Context vs sibling CY-1Division: CY-2
scores slightly less and draws less (22.8% vs ~26%). The home edge
is small and unstable by season (+0.09, +0.02, −0.03, +0.56, +0.06,
0.00) — the 2024/2025 +0.56 is a single-season outlier, not a
level shift; the DC fit estimates home advantage per fit, it is not
hard-coded.

## Findings

**F1 — League levels drift by season.** Goals per match move
2.39 → 2.77 across full seasons (±0.4). Verdict: **SIGNAL**
(descriptive fact). Design consequence: per-league levels with
time-decayed fitting, as in production; no cross-league level
borrowing beyond shrinkage priors for thin leagues.

**F2 — Goals traits are moderately reliable.** Career split-half r
(team-season odd/even halves, n = 80 team-seasons): goals-for
**0.43**, goals-against **0.48**. Weaker than J1 (0.71 / 0.59) —
this is a high-turnover second tier with only 29–30 matches per
team-season — but clearly above zero: a ratings architecture has
real, persistent team signal to capture. Verdict:
**SIGNAL-CANDIDATE (moderate)**. This is the green light for a
goals model; nothing else has a target.

**F3 — Half shares are noise.** True variance of the per-match
first-half goals share (observed variance minus the binomial noise
floor, pre-virgin event matches n = 630): **−0.0049** — below the
floor. Frozen constant: 1H share of goals **0.4351** (ratio of
sums). Verdict: **NOISE.** Halves presentation, if ever wanted,
uses the frozen constant exactly as production does. This book
stays closed.

**F4 — The cross-tier gap is SMALL and asymmetric.** Relegated-in
teams (previous season in CY-1Division, n = 8 team-seasons over the
three pre-virgin transitions): GF **1.386** vs league 1.311
(**+0.08**), GA **1.104** vs 1.311 (**−0.21**), PPG 1.556 vs 1.396
(+0.16). The defensive edge is the real part (~2 SE at this n);
the attacking edge is within noise. For contrast, promoted-out
teams in their last CY-2 season (n = 10) were dominant
(GF 1.608, GA 0.820, PPG 1.973) — the promotion cut falls far
above the league mean, so the relegation cut falling only just
above it is the informative asymmetry: CY-1's bottom teams are
roughly CY-2-average sides. Brand-new ids (n = 10) are NOT weak
on arrival (GF 1.389, GA 1.352, PPG 1.368 ≈ league) — several are
strong returning/ambitious clubs (AEZ Zakakiou 1.93 PPG,
Digenis Morphou 1.76) — so no new-team penalty is assumed.
Verdict: **SIGNAL-CANDIDATE (weak, defence-led)**. Justifies ONE
gated X2 arm with the measured magnitudes (attack +0.08,
defence −0.21 goals/match), not a J1-sized ±0.5 offset. The gate
adjudicates; Gate Zero ships if X2 does not beat it.

**F5 — Feasibility boundary (fact).** Goals is the ONLY buildable
candidate. SOT / corners / total shots: no stats feed in any
season, so no target exists and no virgin window could contain
one. Cards: the event feed omits plain yellows (0 in 1,210
payloads); the only card events are YellowRed (51) and straight
Red (86) — a rare-event count, not a yellow-cards target.
Referee: empty in all payloads. xG / shotmap / lineups: absent.
Per the locked design rule, model scope is set per league by this
matrix — a scores-only league gets a goals model only.
