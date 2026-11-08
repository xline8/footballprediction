# Phase 3 — EDA: Austria 2. Liga (2021/2022 – 2026/2027)

Computations: `eda.py` (digest in `eda_summary.json`). Sample: 1,266
matches, 27 teams. Standard, as in J1: **a trait is a signal
candidate only if it reproduces on disjoint halves of the same
teams' matches (split-half, career-pooled, ≥24 team-matches, 30
seeded splits) or survives a variance decomposition against its
sampling-noise floor.**

## Levels

| Quantity (per match) | AT-2Liga (complete seasons) | AT-Bundesliga | J1 |
|---|---|---|---|
| Goals | 2.91 (SD 1.69) | 2.81 | 2.55 |
| Home / away goals | 1.55 / 1.36 | 1.52 / 1.29 | 1.38 / 1.18 |
| Home win / draw / away win % | 43.7 / 22.6 / 33.7 | 39.5 / 27.5 / 33.0 | 41.3 / 26.8 / 31.9 |
| BTTS % / Over 2.5 % | 54.7 / 56.4 | 56.6 / 53.3 | 50.4 / 47.0 |
| Total shots | 18.6 (feed-contaminated — F12) | 24.9 | 24.8 |
| SOT | 9.80 (feed-contaminated — F12) | 8.52 | 8.08 |
| Corners | 9.81 | 9.76 | 9.47 |
| Yellow cards (events) | 4.90 | 4.07 (stats) | 2.34 |
| Red cards (events) | 0.24 | 0.235 | 0.11 |

The second tier out-scores its parent (2.91 vs 2.81 goals, over-2.5
56.4%) with a bigger home edge (+0.19 goals) and European-level
discipline (4.90 event yellows — higher than the Bundesliga's 4.07
stats yellows; the sources differ, events vs stats, so the gap is a
descriptive note, not a precise comparison). The clean-era shot
levels (excluding the contaminated 2024/2025) are ≈17–18 total
shots and ≈8.6 SOT per match — well below the parent's 24.9 / 8.52
shots/SOT pairing, i.e. this feed counts shots more narrowly than
the Bundesliga feed even in its clean era. The virgin season
(2025/2026) ran cooler than dev on every counting stat (goals 2.65,
SOT 7.85, corners 8.99, yellows 4.39) — the gates will feel that.

Dispersion (variance/mean of match total, complete seasons): goals
0.98, corners 1.16, yellows 1.00 — near-Poisson. SOT 3.61 and total
shots 2.68 are **not** read as overdispersion: they are inflated by
mixing the two feed definitions of F12.

## Findings

**F1 — League levels drift by season.** Goals by season: 3.05, 2.90,
2.98, 2.95, 2.65 (complete seasons); corners 10.43 → 8.99 across the
span; yellows 4.70–5.53 with the virgin season lowest (4.39). Home
edge +0.19 goals pooled. Verdict: **SIGNAL** (descriptive fact) —
per-league levels with time-decayed fitting, as in production.

**F2 — Core team traits are reliable.** Career split-half r:
shots-for 0.816 / shots-against 0.814, SOT-for 0.746 / 0.777,
corners-for 0.617 / 0.766, goals-against 0.753, goals-for 0.472,
event-yellows-for 0.445 / 0.574, possession-for 0.817 / 0.804.
Verdict: **SIGNAL-CANDIDATE** — a ratings architecture has real
signal in every market here. Goals-for (0.472) is the weakest of
the counting traits, as is common at this tier; goals-against is
strong (0.753).

**F3 — Half shares are noise for goals; the constants are frozen
from event times.** True variance of the per-match 1H share
(observed minus binomial floor), all event matches: goals
**−0.0011** (at/below the floor — NOISE), yellows **+0.0033** (a
small positive excess, ≈5% of the observed variance — no team-level
halves model is licensed by it, and none is built anywhere in this
program). Team-level 1H goal-share split-half r = 0.177 (weak).
League constants (ratio of sums, event-derived): **goals 0.4543,
yellows 0.3430**. Verdict: **NOISE for modelling; constants frozen
for presentation.** SOT, corners and total shots have **no halves
source at all** in this league (no period splits; shots and corners
leave no event trace) — those markets are FT-only, per the RU-1
precedent. Cards *do* have an event-time source, so the yellows
constant above is legitimate and frozen; goals likewise.

**F4 — Movers, measured against the real parent corpus, by entrant
class.** Entrants into the 2. Liga per season were classified by
where they actually came from (Bundesliga membership read from the
league_id-38 warehouse corpus by team id): **relegated from the
Bundesliga** (n=4 entrant-seasons through 2025/2026: Admira 10053
in 2022/2023, Ried 10017 in 2023/2024, Austria Lustenau 9982 in
2024/2025, Austria Klagenfurt 10009 in 2025/2026; BW Linz 2433
arrives in the reserved 2026/2027 and is excluded) — first-
season gaps vs league mean: **GF −0.06, GA −0.29** (relegated clubs
score at league average but concede notably less — they arrive
defensively strong); **from below / returning** (n=10, incl.
returning B-teams Sturm Graz II 1921, Rapid Wien II 1952, Austria
Wien II 10248): **GF −0.12, GA +0.05** (mildly weak both ways).
B-teams are never in the relegated-from-Bundesliga class and can
never move up — they enter/leave only via the Regionalliga.
Verdict: **SIGNAL (weak, small-n)** — the gaps are real in
direction (parent-tier clubs defend better on arrival) but the
samples are 4 and 10 entrant-seasons, far too thin to hard-code an
offset. The goals candidate therefore carries the template-
sanctioned **shrinkage arm** (thin-data teams pulled toward the
league mean) motivated by this measurement, exactly as RU-1 did —
no X2 offset is estimated or imported.

**F5 — Set-play xG share: NOT MEASURABLE.** No xG exists in this
feed. Verdict: **DATA ABSENT** (feature dropped at Phase 3.5).

**F6 — Shot quality / finishing / on-target rate: NOT MEASURABLE.**
No shotmap, no xG. The SOT model's quality-input and xGOT arms of
the J1 template cannot exist here. What remains measurable is
volume: shots-for trait r = 0.816 (F2) is the SOT architecture's
total-shots signal, carried inside Gate Zero itself. Verdict:
**DATA ABSENT** for X4/X6; no standalone on-target-rate covariate
is built (it would be unmeasurable *and* is rejected on principle
— J1 F6 measured it as NOISE where it could be measured).

**F7 — xGOT: NOT MEASURABLE** (no shotmap). **DATA ABSENT.**

**F8 — Referee strictness: NOT MEASURABLE.** Referee text is empty
in 1,266/1,266 payloads (coverage 0.0%, every season including the
virgin). Verdict: **DATA ABSENT** — the cards candidate runs Gate
Zero only; there is no referee fallback question to answer.

**F9 — Territorial pressure: possession is the only covariate the
feed offers.** Team possession trait r = 0.817 / 0.804 (the joint-
strongest trait in this EDA); per-match, home corners correlate
0.305 with home possession (n=1,254). `touches_opp_box` and
`big_chance` are **absent from every payload** — the X7 box-touch
arm and the big-chance half of the production X9 pair cannot
exist. Verdict: **SIGNAL-CANDIDATE (possession only)** — the
corners Gate Zero is the production pattern with the
possession-only territorial covariate (the RU-1 construction);
no variant arm is registered for corners.

**F10 — Star absence: not re-run; the question stays closed.** The
V10 protocol produced a null on the top-5 and replicated nulls
elsewhere; nothing in this EDA reopens it (lineups exist in the
payload but carry no new reliability evidence). Lineup/absence
features remain forbidden.

**F11 — xG calibration: NOT MEASURABLE** (no xG). The goals model
is goals-only by construction; there is no blend era and no
goals-only era — there is only goals.

**F12 — Feasibility boundary + the feed definition break (fact).**
Buildable: all five candidates — goals (1,266 matches), SOT /
corners / total shots (1,254 with stats; dev n=708, virgin n=210),
cards (event yellows, 1,266; dev n=720, virgin n=210). The
2024/2025 shot/SOT definition break (Phase 1 quirk 3) sits inside
the dev window for S-AT2 and T-AT2 and in the trailing state that
opens their virgin seasons; it is recorded here and in both
preregs, and the gates — not window surgery — decide those
candidates.
