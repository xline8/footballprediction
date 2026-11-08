# NL Tweede Divisie — exploratory findings

All figures below are descriptive measurements from `eda_summary.json`
(`inventory.py`); no model is fitted and no virgin outcome is used
for arm selection. 2025/2026 levels are design-level aggregates only.

## F1 — levels and home advantage

| season | goals | home goals | away goals | H/D/A % | BTTS % | over 2.5 % | over 3.5 % |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2021/2022 | 3.07 | 1.72 | 1.36 | 50.3 / 19.6 / 30.1 | 55.2 | 59.5 | 35.3 |
| 2022/2023 | 3.20 | 1.74 | 1.46 | 45.1 / 21.2 / 33.7 | 58.2 | 61.1 | 40.2 |
| 2023/2024 | 3.16 | 1.62 | 1.53 | 38.9 / 23.2 / 37.9 | 60.8 | 62.1 | 38.9 |
| 2024/2025 | 3.32 | 1.77 | 1.55 | 43.8 / 18.0 / 38.2 | 58.8 | 64.1 | 43.5 |
| 2025/2026 | 3.34 | 1.83 | 1.52 | 46.7 / 19.6 / 33.7 | 61.4 | 66.0 | 42.8 |
| 2026/2027 (partial, n=108) | 3.62 | 1.94 | 1.68 | 42.6 / 19.4 / 38.0 | 67.6 | 72.2 | 48.1 |

Pooled goals are 3.24 per match and the home-goal minus away-goal
mean is **+0.25** — a normal home advantage, smaller than the
Eredivisie's and close to the Eerste Divisie's +0.32. Goals drift
upward across the five complete seasons (3.07 → 3.34) and the
over-2.5 rate rises with them (59.5% → 66.0%). The pooled over-2.5
rate is 63.2% — high, and high in every single season: the OU2.5
leg that has killed most goals candidates in this program will be
hard here too, because the base-rate baseline is itself strong.
Reference points: J1 pooled ~2.7 goals, Eredivisie ~3.1, Eerste
Divisie ~3.11. Tweede Divisie is the highest-scoring Dutch tier in
the warehouse.

## F2 — team-trait reliability (goals)

Pooled random split-half r (60 repetitions; teams with at least 24
team rows): goals for **0.747**, goals against **0.714** — SIGNAL,
in line with J2/J3 (0.66–0.69) and the Eerste Divisie (0.82/0.69).
Season-by-season split-half r (min 8 team rows) ranges 0.32–0.74
for, 0.32–0.64 against: noisier within a single 34-match season,
as expected, but the pooled trait is real. A scores-only ratings
fit has genuine signal — this is the entire justification for
building a goals model where no other market can exist.

## F3 — half shares and true variance (goals only)

Goals from events across all seasons: 1H share **0.436** (ratio of
sums, n = 1,582 matches with goals > 0; 56 goalless matches carry
no share). Observed per-match share variance 0.0931; binomial
noise floor (pooled league share, per-match — the corrected form,
not the plug-in per-match share which understates noise when most
matches have 1–3 goals) 0.0986; **true variance −0.0054**, i.e. at
or below zero. Team split-half r of the 1H share is **−0.13**.
Conclusion, same as every league in the program: the per-match 1H
share is pure noise around a frozen league constant. The constant
is **0.436** for reporting splits only; no team or per-match halves
feature exists. (SOT/corners/cards/total-shots half shares do not
exist — no stats feed.)

## F4 — movers and X2 evidence

Entrants per transition (clubs absent from this league the prior
season) and their first-season gaps vs the league team-goal mean:

| transition | entrants | GF gap | GA gap |
|---|---|---:|---:|
| into 2022/2023 | Lisse, OFC Oostzaan | −0.43 | +0.49 |
| into 2023/2024 | ACV, ADO '20, GVVV Veenendaal, Jong Almere City FC | +0.01 | −0.02 |
| into 2024/2025 | Barendrecht, RKAV Volendam | +0.08 | +0.28 |
| into 2025/2026 (virgin transition, descriptive only) | Hoek, IJsselmeervogels, Kozakken Boys | −0.20 | −0.14 |
| into 2026/2027 (partial, descriptive only) | Kloetinge, Rohda Raalte | −0.77 | +1.10 |

No entrant in any transition played in the Eerste Divisie the
previous season (0/13) — entrants come from below (Derde Divisie)
or are reserve sides, so the expected direction is weaker, not
stronger. Pooled over the three **dev** transitions only (n = 256
entrant team-matches; the virgin transition is deliberately
excluded from the frozen magnitudes so no virgin outcome sets an
arm parameter): GF gap **−0.093**, GA gap **+0.181**. The direction
matches the below-tier expectation on both sides, but the
magnitudes are small (GF ≈ 1.3 SE, GA ≈ 2.6 SE) and the
per-transition signs flip — far weaker than J1's ±0.5 or the
Eerste Divisie's +0.42/−0.20. Verdict: **SIGNAL-WEAK — X2 is
adopted as a gated variant arm only**, with the pooled dev
magnitudes frozen in the prereg; the gate decides, and a FAIL
there costs nothing.

## F5 — Jong (reserve-side) behavior

Three Jong sides appear in the corpus (Jong Almere City FC, Jong FC
Volendam, Jong Sparta Rotterdam). Their goals-for/against
split-half r is 0.67/0.60 vs 0.75/0.73 for non-Jong — no material
reliability contrast (unlike the Eerste Divisie, where Jong
goals-against reliability collapsed to 0.15). Jong goal variances
are higher (GF 2.36 vs 1.76, GA 2.08 vs 1.80), consistent with
youth sides being more volatile, but with only 3 teams this is
descriptive. No Jong-specific feature is adopted; Jong clubs enter
the fit like any other club, and Jong entrants are included in the
X2 mover set on the same terms.

## F6 — red cards

Red-family events total 238 (0.145/match; 211 matches contain at
least one red). Team split-half r for reds is **−0.09** — noise.
Yellows do not exist at all (0 events). No cards candidate of any
kind is buildable; reds are not a target (rare event, no
reliability) and not a covariate.

## F7 — missing xG/shotmap and target implications

There is no expected-goals key, no shotmap, no stats block, no
lineup, and no referee text in any season. xG blend, set-play xG,
xG/shot, xGOT, box touches, possession, referee strictness, and
lineup/absence features are all unavailable. SOT, corners, cards,
and total shots are not feasible count targets. Goals is the only
candidate.

## F8 — design boundary

No fitting, preregistration, engine, or virgin read was performed.
The complete 2025/2026 levels are included only as the same
design-level aggregate allowed in the brief.
