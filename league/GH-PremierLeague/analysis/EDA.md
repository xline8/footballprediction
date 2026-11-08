# Step 3 — EDA: Ghana Premier League (FotMob 522)

All numbers are on **eligible** matches (not awarded; n=1,596)
unless stated otherwise, from `eda_numbers.json` (re-derived from
the payloads; inventory in `inventory_summary.json`). Reference
points: J1 goals 2.68/match, home-win rate ~.44; NG goals
2.11/match, home-win .652; RU2 goals 2.21–2.87/match.

## 1. Levels per season

| season | n | mean goals | H / D / A | O2.5 | BTTS | 0-0 |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2021/2022 | 306 | 2.04 | .536 / .301 / .163 | .307 | .402 | .121 |
| 2022/2023 | 306 | 2.11 | .595 / .248 / .157 | .356 | .395 | .124 |
| 2023/2024 | 305 | 2.05 | .584 / .249 / .167 | .334 | .367 | .108 |
| 2024/2025 | 290 | 1.88 | .559 / .269 / .172 | .286 | .348 | .134 |
| 2025/2026 | 299 | 2.03 | .575 / .268 / .157 | .341 | .348 | .157 |
| 2026/2027 (partial, rounds 1–10) | 90 | 2.03 | .600 / .244 / .156 | .389 | .422 | .122 |
| **Pooled eligible** | **1,596** | **2.02** | **.571 / .266 / .163** | **.329** | **.375** | **.128** |

Reference reading:

- **Ghana is the lowest-scoring league built so far: 2.02
  goals/match pooled** (vs NG 2.11, J1 2.55–2.68). Home teams score
  1.35 vs away 0.67 per match, win **57.1%** of eligible matches and
  lose only 16.3%. Over-2.5 sits at 28.6–35.6% in full seasons — the
  OU2.5 base rate is far below the top-5 (~50%).
- **2024/2025 is the low season (1.88)** — and it is low *after*
  removing the 15 awarded 3-0s, which had inflated the raw figure to
  1.93; the awarded rows were 45 goals of pure forfeit. No season
  effect is fitted; the season is scored as-is in dev.
- The in-progress 2026/2027 (n=90) sits on the pooled levels
  (2.03 goals, 60.0% home wins) — a partial-season sample, not a
  trend claim; it is the reserved confirmatory window, not
  interpreted here.

SOT / corners / cards / total shots: **no levels exist** — the targets
are absent from every payload (DATA_UNDERSTANDING.md §2/§4). There is
nothing to tabulate, and no proxy is constructed.

## 2. Team trait reliability (the J1 checklist, goals only)

Split-half by season: each team's matches split chronologically into
halves; Pearson r of per-match rates across halves (teams ≥10 matches,
≥5 per half); pooled across seasons.

| trait | 21/22 | 22/23 | 23/24 | 24/25 | 25/26 | 26/27* | pooled |
|---|---:|---:|---:|---:|---:|---:|---:|
| goals for | .069 | −.323 | −.029 | −.183 | .317 | .030 | **−.028** |
| goals against | .282 | .572 | .227 | .617 | .575 | .183 | **.320** |

\* 2026/2027 partial (18 teams qualify on a 10-round split); shown for
completeness, not used in any decision.

Team goal traits are **split: attack is trait-free, defence is
moderately reliable**. Goals-for split-half r is −0.03 pooled —
zero, and negative in three of five full seasons: within a ~34-match
season split into ~17-match halves, a team's scoring rate in one
half does not predict the other half at all. That is weaker than NG
(.168) and far below the J1 career-pooled figures. Goals-against is
better (r=.32 pooled, positive in every season, .57–.62 in three of
them): defensive strength persists within a season while attacking
output does not. Two readings are both live and the dev gate will
adjudicate between them: (a) Ghanaian attacking strength genuinely
varies fast within a season (form, not trait); (b) the DC ratings
will be mostly noise on the attack side and the model will struggle
to beat climatology. Either way, **no trait-based feature is adopted
on this evidence** — the goals model uses only the DC ratings
themselves, which are the §2 architectural component, not a
covariate claim.

## 3. Home advantage

Home goals 1.35 vs away 0.67 pooled (ratio 2.01:1); home-win rate
57.1% vs away-win 16.3%. The fitted DC home parameter will absorb
this; no separate home-advantage feature is needed or used. Note the
awarded rows would have overstated it (15 home 3-0s vs 8 away 3-0s
among the 23) — they are excluded before this table.

## 4. Half shares (the frozen-constant question)

HT goals from Half events (1,408 trusted HT rows; the 4 `ht_suspect`
matches excluded).

| season | HT coverage | 1H share (ratio of sums) |
|---|---:|---:|
| 2021/2022 | 273/306 | 0.4631 |
| 2022/2023 | 268/306 | 0.4537 |
| 2023/2024 | 273/305 | 0.4704 |
| 2024/2025 | 255/290 | 0.4391 |
| 2025/2026 | 259/299 | 0.4835 |
| 2026/2027 | 80/90 | 0.4590 |
| **Pooled** | **1,408/1,596** | **0.4622** |

- **Frozen goals constant: 0.4622** (pooled ratio of sums; 1,487 HT
  goals / 3,217 FT goals over the trusted HT rows).
- **The per-match 1H share is noise**: observed variance of the
  per-match 1H share 0.14577 vs the binomial noise floor 0.14667 —
  excess variance **−0.0009**, i.e. at or below the floor, exactly
  the finding that closed the halves book in production. Team-level
  1H-share split-half r = **−0.053** (94 team-seasons) — no team
  tendency. The constant is presentation only, never fitted, never
  per-team.
- **Level note**: Ghana scores 46.2% of its goals before half-time —
  between J1 (0.412) and the NPFL (0.4796), close to RU2 (0.4393).
  That is a league-level fact, not a modelling input beyond the
  constant.

## 5. Turnover / movers

New clubs per season (teams present in season S, absent in S−1):
2022/2023: 4 (Kotoku Royals, Nsoatreman, Samartex, Tamale City);
2023/2024: 3 (Bofoakwa Tano, Heart of Lions, Nations FC); 2024/2025:
3 (Holy Stars, Vision FC, Young Apostles); 2025/2026: 3 (All Blacks,
Eleven Wonders, Hohoe United); 2026/2027: 3 (Ashanti Gold, Debibi,
Port City). Every season brings 3–4 promoted sides from Ghana
Division One (not in the warehouse, unbuilt). They enter the DC fit
at the league mean in Gate Zero; the SHRINK arm (MODEL_DESIGN §2)
is the sanctioned thin-data treatment. No cross-league mover prior
exists (no built Ghanaian sibling), so no X2 offset is estimated.

Two promoted sides then withdrew mid-season and were forfeited out:
Nsoatreman (promoted 2022/2023) withdrew during 2024/2025 and
Hohoe United (promoted 2025/2026) withdrew during 2025/2026 — see
DATA_UNDERSTANDING.md §5. Their awarded rows are excluded, so the
withdrawals do not contaminate the ratings; their played matches
stay in the fit as ordinary results.
