# IR Persian Gulf Pro League — exploratory findings

All figures below are descriptive measurements from `eda_summary.json`
(`compute_summaries.py`, read off the built CSV); no model is fitted
and no virgin outcome is used for arm selection. 2025/2026 levels are
design-level aggregates only, and the season is partial (rounds 1–23,
n = 178). Played league n = 1,243 (the two Asian Qualifiers
playoff rows are excluded everywhere).

## F1 — levels and home advantage

| season | n | goals | home goals | away goals | H/D/A % | BTTS % | over 2.5 % | over 3.5 % |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2021/2022 | 240 | 1.81 | 0.94 | 0.87 | 34.2 / 36.7 / 29.2 | 36.2 | 29.2 | 9.6 |
| 2022/2023 | 240 | 2.00 | 1.13 | 0.87 | 36.7 / 35.8 / 27.5 | 38.8 | 31.7 | 19.6 |
| 2023/2024 | 240 | 2.18 | 1.12 | 1.06 | 37.1 / 31.7 / 31.2 | 43.3 | 35.0 | 20.8 |
| 2024/2025 | 240 | 1.98 | 1.08 | 0.90 | 37.5 / 34.2 / 28.3 | 38.3 | 30.8 | 14.2 |
| 2025/2026 (partial) | 178 | 1.82 | 1.03 | 0.78 | 39.9 / 36.0 / 24.2 | 37.6 | 28.7 | 12.4 |
| 2026/2027 (partial, n=105) | 105 | 1.99 | 1.15 | 0.84 | 36.2 / 37.1 / 26.7 | 40.0 | 32.4 | 12.4 |

Pooled dev (2021/2022–2024/2025, n = 960): 1.99 goals/match,
home win 36.4%, draw 34.6%, over-2.5 31.7%. Scored dev
(2022/2023–2024/2025, n = 720): 2.05 goals/match, over-2.5 32.5%
(234/720). Home advantage (home minus away goals per match) runs
+0.08 / +0.27 / +0.05 / +0.19 in the dev seasons — a **weak** home
edge by program standards (pooled dev +0.15, vs ~+0.3–0.4 in most
leagues), and it nearly vanishes in 2021/2022 (+0.08) and 2023/2024
(+0.05). The DC fit's home-advantage parameter will be fitted, not
assumed — but the prior expectation is a small one.

Two things stand out against the program's reference points (J1
~2.7 goals/match, Tweede Divisie 3.24, Eredivisie ~3.1):

1. **The Persian Gulf Pro League is one of the lowest-scoring
   leagues in the program** (dev 1.99 — a touch above the Azadegan
   sibling's 1.89, far below J1), and its over-2.5 rate sits at
   29–35% in every season. The virgin window (partial, 1.82,
   28.7% over-2.5) is lower-scoring than scored dev (2.05,
   32.5%) — a mild regime shift in the same direction as the
   sibling's, and exactly what the calibration leg is for. But
   note the virgin is rounds 1–23 only: late-season matches
   (rounds 24–30, where relegation pressure concentrates) are
   missing from the warehouse, so the virgin read tests the
   model on the early/mid season, not the full season.
2. **Draws are frequent** (34.6% pooled dev, 36.0% in the virgin
   window) and home wins modest — the 1X2 distribution is flatter
   than in most leagues, which compresses what ratings can win
   over climatology on RPS. This is the same shape as Azadegan
   (35.2% draws), whose goals model failed its dev gate on the
   OU2.5 leg — the Persian Gulf build starts from the same
   warning, not from optimism.

## F2 — team-trait reliability (goals)

Pooled split-half r across team-seasons (min 8 matches):

| trait | chronological split r | random split-half, 60 reps (mean, range) |
|---|---|---|
| goals for | **0.368** (n = 98 team-seasons) | 0.452 (0.32–0.59) |
| goals against | **0.519** (n = 98) | 0.398 (0.24–0.55) |

Season-by-season chronological r (min 8 team rows): GF
0.57 / 0.55 / 0.25 / 0.79 / 0.38 / 0.04 (2021/2022–2026/2027;
2026/2027 partial, meaningless at 12 rounds); GA 0.52 / 0.70 /
0.59 / 0.72 / 0.05 / 0.50 (the 2025/2026 GA 0.05 is the partial
season — 23 rounds split 11/12 — not a regime statement).

Verdict: **MIXED — GA is SIGNAL, GF is WEAK-MODERATE.** Defensive
team quality persists across a season about as well as in J2/J3
(0.62–0.68 pooled there) and the Azadegan sibling (0.51);
attacking quality is less stable (sibling GF 0.27; here 0.37
chronological, 0.45 random-split — a little better than the
sibling, still well below J2/J3's 0.66–0.69). A scores-only ratings
fit has real signal — carried disproportionately by the defensive
side — but less than in most program leagues, and the per-season
GF numbers swing wildly (0.25 in 2023/2024, 0.79 in 2024/2025).
The DC fit's attack ratings will be noisier here than the program
is used to; the dev gate, not optimism, decides whether that is
enough.

## F3 — half shares and true variance (goals only)

Goals from events across all seasons: 1H share **0.4271** (ratio of
sums, 1,031/2,414; n = 1,233 matches with a usable HT split).
Per-season shares: 0.417 / 0.425 / 0.428 / 0.434 / 0.445 / 0.408
(partial). Observed per-match share variance 0.13734; binomial
noise floor (pooled league share, per-match) 0.14094; **true
variance −0.0036**, i.e. at or below zero. Team split-half r of
the 1H share is **+0.087** (n = 98 team-seasons).

Conclusion, same as every league in the program: the per-match 1H
share is pure noise around a frozen league constant. The constant
is **0.427** for reporting splits only; no team or per-match halves
feature exists. (SOT/corners/cards/total-shots half shares do not
exist — no stats feed.) The per-season wobble (0.445 in the partial
2025/2026 vs 0.408 in the partial 2026/2027) is sampling noise on
~180–240 matches a season, consistent with the variance
decomposition — not a trend to model.

## F4 — entrants and the case for a mover prior

Entrants per transition (clubs absent from this league the prior
season) and their first-season gaps vs the league team-goal mean:

| transition | entrants | GF gap | GA gap |
|---|---|---|---|
| into 2022/2023 | Malavan, Mes Kerman | −0.267 | +0.283 |
| into 2023/2024 | Esteghlal Khuzestan, Shams Azar Qazvin | +0.010 | +0.194 |
| into 2024/2025 | Kheybar Khorramabad, Chadormalu Ardakan SC | −0.223 | −0.006 |
| into 2025/2026 (virgin transition, descriptive only) | Paykan, Fajr Sepasi | −0.038 | +0.136 |
| into 2026/2027 (partial, descriptive only) | Sanat Naft Abadan, Nassaji Mazandaran FC, Mes Shahr Babak | −0.397 | +0.404 |

Pooled over the three **dev** transitions only (n = 6 entrant
teams, 180 entrant team-matches; the virgin transition is
deliberately excluded from any frozen magnitude so no virgin
outcome sets an arm parameter): GF gap **−0.160**, GA gap
**+0.157**.

Verdict: **WEAK BUT DIRECTIONAL — there is a small, estimable
entrant prior.** Unlike the Azadegan sibling (pooled gaps +0.002 /
−0.034 — no signal at all), Persian Gulf entrants arrive below the
league mean on both sides of the ball: they score ~0.16 fewer and
concede ~0.16 more per match. Five of the six per-transition gaps
point in the "worse" direction; the virgin transition (GA +0.136)
and the 2026/2027 expansion transition (GF −0.397 / GA +0.404)
point the same way. The magnitude is small (n = 6 teams, so the
standard error on each pooled gap is ~±0.11 — the gaps are only
~1.4 SE from zero) and far below J1's ±0.5 — but it is the only
entrant magnitude the data supports, it is frozen from dev
transitions only, and the pre-registered X2 arm exists precisely so
the dev gate can judge it instead of this document asserting it.
What is NOT estimable is a rating-based variant: an offset per
entrant from its Azadegan League rating would rest on the sibling
goals model, which **failed its dev gate and shipped no fitted
ratings**, and on a cross-league scaling fitted from 6 teams. The
X2 arm is therefore the flat frozen offset (MODEL_DESIGN.md),
not an Azadegan-rating prior. Entrants start at the league mean in
Gate Zero and SHRINK, and at the frozen offset in X2 only.

## F5 — format churn

23 distinct team ids across six seasons; only ~14 clubs are present
in most seasons. Two clubs turn over per season through 2025/2026
(then 1 out / 3 in at the 2026/2027 expansion), so at every season
start roughly an eighth of the league has no in-league history and
starts at the league mean (or the X2 offset) under season-blocked
fitting. That is a structural feature of this league, not a data
gap. The 18-team 2026/2027 expansion changes the denominator of a
season (306 matches when complete, vs 240) but not the per-match
structure; nothing is imputed for the missing 2025/2026 rounds
24–30.

## F6 — cards (a feed break, not a target)

Yellow events total 1,080 in 407 matches — **all of them in the
last two seasons** (749 in 178 league matches in 2025/2026,
4.21/match, 175/178 matches with a yellow event; 331 in 105 in
2026/2027, 3.15/match). In 2021/2022–2024/2025 there are **zero**
Yellow events in 960 matches — the event feed simply did not carry
them, as the red-family ramp shows (Red + YellowRed per match:
0.096 → 0.129 → 0.188 → 0.233 in the same seasons, then 0.242 /
0.219 once yellows appear). Team split-half r for yellows in the
single usable season (2025/2026) is **0.452** (n = 16) — suggestive
that yellow-taking persists within a season — and for reds pooled
is **0.194** (per-season −0.28 / +0.06 / +0.36 / +0.14 / +0.13 /
+0.16, sign-flipping noise, and the early seasons are
under-captured anyway).

No cards candidate of any kind is buildable: there is no yellows
target in any dev season and no virgin-adjacent dev window in
which a cards model could be walk-forward validated (the only
season with yellow coverage IS the virgin window, and a model
cannot be both fitted and validated on one partial season). The
yellow reliability number is recorded here as a single-season
observation for a future build if the feed ever extends backwards,
not as a gate input. Reds are a rare-event count with no
reliability evidence. Reds are not a target and not a covariate.

## F7 — missing xG/shotmap and target implications

There is no expected-goals key, no shotmap, no stats block in any
season, and no lineup or referee text in any dev season. xG blend,
set-play xG, xG/shot, xGOT, box touches, possession, referee
strictness, and lineup/absence features are all unavailable. SOT,
corners, and total shots have no target in any season, including
the virgin window — none of them is a candidate, and none can
become one without new data. Cards have a target only in the
virgin window itself, which cannot validate a model. The goals
candidate is the only buildable one, and it is goals-only by
necessity: the reference blend's xG half never exists here.
