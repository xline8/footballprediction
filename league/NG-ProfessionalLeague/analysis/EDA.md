# Step 3 — EDA: Nigeria Professional Football League (FotMob 533)

All numbers are on **eligible** matches (finished, non-awarded, not
Championship Group; n=1,813) unless stated otherwise, from
`eda_numbers.json` (re-derived from the payloads; inventory in
`inventory_summary.json`). Reference points: J1 goals 2.68/match,
home-win rate ~.44; RU2 goals 2.21–2.87/match, home-win ~.40–.45.

## 1. Levels per season

| season | n | mean goals | H / D / A | O2.5 | BTTS | 0-0 |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2021/2022 | 379 | 2.05 | .713 / .208 / .079 | .368 | .375 | .090 |
| 2023 (group stage) | 180 | 2.11 | .523 / .328 / .139 | .349 | .456 | .089 |
| 2023/2024 | 379 | 2.24 | .692 / .226 / .082 | .368 | .425 | .090 |
| 2024/2025 | 380 | 2.06 | .642 / .247 / .111 | .340 | .395 | .100 |
| 2025/2026 | 379 | 2.02 | .633 / .248 / .119 | .338 | .383 | .119 |
| 2026/2027 (partial, rounds 1–12) | 116 | 2.34 | .569 / .336 / .095 | .405 | .491 | .129 |
| **Pooled eligible** | **1,813** | **2.11** | **.652 / .247 / .101** | **.356** | **.399** | **.100** |

Reference reading:

- **The NPFL is a low-scoring, extreme-home-advantage league.**
  2.11 goals/match pooled (vs J1 2.68); home teams score 1.50 vs
  away 0.61 per match, win **65.2%** of eligible matches and lose
  only 10.1%. Away wins are rare in every season (7.9–13.9%).
  Over-2.5 sits at 33.8–36.8% in full seasons — the OU2.5 base rate
  is far below the top-5 (~50%).
- **2023 group stage is the outlier season**: home-win rate drops to
  52.3% and draws jump to 32.8% (vs ~21–25% elsewhere), while goals
  stay ordinary (2.11). The two-group format (each team plays only
  its own group's 9 opponents home and away) plausibly compresses
  the table; whatever the cause, the season is scored as-is in dev —
  no season effect is fitted.
- The in-progress 2026/2027 (n=116) is higher-scoring (2.34) and
  draw-heavier (33.6%) — a partial-season sample, not a trend claim;
  it is the reserved confirmatory window, not interpreted here.

SOT / corners / cards / total shots: **no levels exist** — the targets
are absent from every payload (DATA_UNDERSTANDING.md §2/§4). There is
nothing to tabulate, and no proxy is constructed.

## 2. Team trait reliability (the J1 checklist, goals only)

Split-half by season: each team's matches split chronologically into
halves; Pearson r of per-match rates across halves (teams ≥10 matches,
≥5 per half); pooled across seasons.

| trait | 21/22 | 2023 | 23/24 | 24/25 | 25/26 | 26/27* | pooled |
|---|---:|---:|---:|---:|---:|---:|---:|
| goals for | .078 | .378 | .278 | .124 | −.008 | −.033 | **.168** |
| goals against | .073 | .526 | .390 | .159 | −.282 | .181 | **.231** |

\* 2026/2027 partial (13 teams qualify); shown for completeness, not
used in any decision.

Team goal traits are **weak** — far weaker than RU2 (.378/.500 pooled)
and far below the J1 career-pooled figures. Within a ~38-match season
split into ~19-match halves, a team's goals-for rate in one half
barely predicts the other half (r=.17 pooled); goals-against is only
slightly better (r=.23). The seed season 2021/2022 is essentially
trait-free (r≈.07/.07). Two readings are both live and the dev gate
will adjudicate between them: (a) NPFL team strength genuinely
varies fast within a season (form, not trait); (b) the DC ratings
will be mostly noise here and the model will struggle to beat
climatology. Either way, **no trait-based feature is adopted on
this evidence** — the goals model uses only the DC ratings
themselves, which are the §2 architectural component, not a
covariate claim.

## 3. Home advantage

Home goals 1.50 vs away 0.61 pooled (ratio 2.46:1); home-win rate
65.2% vs away-win 10.1%. The fitted DC home parameter will absorb
this; no separate home-advantage feature is needed or used. Note the
2023 group-stage dip (home-win 52.3%) and the Championship Group
reversal (home-win 20.0%, home goals 0.93 < away 1.13) — the latter
is why the Championship Group is excluded (DATA_UNDERSTANDING.md
§3), the former is scored as-is.

## 4. Half shares (the frozen-constant question)

HT goals from Half events (1,645/1,813 eligible matches, 90.7%).

| season | HT coverage | 1H share (ratio of sums) |
|---|---:|---:|
| 2021/2022 | 348/379 | 0.4814 |
| 2023 | 166/180 | 0.5079 |
| 2023/2024 | 348/379 | 0.4700 |
| 2024/2025 | 344/380 | 0.4756 |
| 2025/2026 | 337/379 | 0.4837 |
| 2026/2027 | 102/116 | 0.4649 |
| **Pooled** | **1,645/1,813** | **0.4796** |

- **Frozen goals constant: 0.4796** (pooled ratio of sums; mean of
  per-match shares 0.4860, n=1,630 matches with ≥1 goal).
- **The per-match 1H share is noise**: split-half reliability of
  team-season 1H shares r = **−0.03** (114 team-seasons) — true
  variance ≈ 0, exactly the finding that closed the halves book in
  production. The constant is presentation only, never fitted,
  never per-team.
- **Level note**: the NPFL scores far more of its goals before
  half-time than J1 (0.412) or RU2 (0.4393) — nearly half its goals
  (48%) come in the first half. That is a league-level fact, not a
  modelling input beyond the constant.

## 5. Turnover / movers

New clubs per season (teams present in season S, absent in S−1):
2023: 4; 2023/2024: 4; 2024/2025: 3; 2025/2026: 4; 2026/2027: 4.
Every season brings 3–4 promoted sides from the Nigeria National
League (not in the warehouse, unbuilt). They enter the DC fit at the
league mean in Gate Zero; the SHRINK arm (MODEL_DESIGN §2) is the
sanctioned thin-data treatment. No cross-league mover prior exists
(no built Nigerian sibling), so no X2 offset is estimated.
