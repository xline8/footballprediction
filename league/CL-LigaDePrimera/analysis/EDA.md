# Step 3 — EDA — CL-LigaDePrimera

Numbers: `analysis/eda_numbers.json` (script `eda_compute.py`,
recomputable from the committed CSV builder). Split-half
reliabilities are per team-season (chronological halves, teams with
>= 10 matches in the season; n = 97 team-seasons).

## Levels per season (per match, both teams)

| season | goals | home | away | SOT | corners | total shots | yellows (stats) | yellows (events) | fouls |
|---|---|---|---|---|---|---|---|---|---|
| 2021 | 2.511 | 1.342 | 1.169 | 8.588 | 9.298 | 25.063 | 3.342 | 4.540 | 24.684 |
| 2022 | 2.567 | 1.488 | 1.079 | 8.431 | 9.393 | 25.941 | 3.971 | 5.229 | 23.782 |
| 2023 | 2.725 | 1.425 | 1.300 | 8.921 | 9.871 | 26.575 | 4.808 | 5.296 | 21.521 |
| 2024 | 2.767 | 1.538 | 1.229 | 9.446 | 9.750 | 26.554 | 5.138 | 5.567 | 22.628 |
| 2025 | 2.646 | 1.550 | 1.096 | 8.704 | 9.651 | 26.642 | 5.250 | 5.413 | 22.671 |
| 2026* | 2.833 | 1.657 | 1.176 | 9.103 | 9.930 | 27.019 | 4.668 | 5.005 | 21.224 |

*in progress. Goals level (2.51–2.77) sits below J1 (~2.7–2.9 era
range is comparable) and well below the top-5 European norm; home
advantage is real every season (home − away = +0.13 … +0.45 goals).
The stats-yellows level *rises* across the era while event yellows
stay ~5.0–5.6 — the two feeds converge but never meet, which is the
artefact quantified in Step 1, not a discipline trend.

## Trait reliability (split-half r, team-season)

| trait | for | against |
|---|---|---|
| goals | 0.283 | 0.350 |
| SOT | 0.315 | 0.357 |
| corners | 0.333 | 0.320 |
| total shots | 0.407 | 0.523 |
| yellows (stats feed) | 0.475 | — |
| yellows (event-unified) | 0.315 | — |
| touches in opp. box | 0.432 | — |

All traits are real but **markedly noisier than J1** (whose headline
traits ran 0.65–0.86): Chile team traits at career scale carry
r ≈ 0.3–0.5. Nothing is at zero, so no target is rejected on
reliability grounds; the gates, not the EDA, decide. Note the stats
yellows look *more* reliable (0.475) than event yellows (0.315) —
reliability does not repair a biased level: the stats feed
undercounts by up to 1.28 cards/match (Step 1), so the target
stays event-unified.

Referee strictness (total event-era yellows per match, referees
with >= 10 matches, n = 33 split referees of 57 named): split-half
r = **0.357** — present but weak, and referee identity is missing
for all of 2021 and ~15% of later matches.

## Half shares — the frozen-constant question

Pooled 1H shares with the noise decomposition
(var_observed vs binomial sampling variance at the pooled share):

| market | source | n | pooled 1H share | true var est. |
|---|---|---|---|---|
| goals | goal events, all seasons | 1,356 | 0.4400 | 0.00000 |
| SOT | period splits, 2023+ | 872 | 0.4456 | 0.00000 |
| corners | period splits, 2023+ | 873 | 0.4644 | 0.00038 |
| total shots | period splits, 2023+ | 873 | 0.4535 | 0.00024 |
| cards | period splits (stats), 2023+ | 865 | 0.3818 | 0.00127 |

Per-match 1H share variance is ≈ pure binomial noise for goals and
SOT and negligibly above it elsewhere — the same verdict as J1 and
the top-5 halves audit. **Frozen league constants are the only
halves mechanism** (presentation only). Cards' constant comes from
the stats splits (the only split source); it is a presentation
share for the event-unified FT prediction, nothing more.
