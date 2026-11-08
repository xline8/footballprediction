# Phase 3 — EDA: Ireland First Division (2021–2026)

Computations: `eda_compute.py` (digest in `eda_numbers.json`).
Population for every number below: **regular-season matches only**
(998), unless labelled otherwise. Dev seasons 2021–2025 (regular
n = 818); virgin 2026 (regular n = 180) contributes only its coverage
inventory — no 2026 row was used for a design decision. Every pattern
below carries a verdict under the halves-audit standard: a trait is a
signal candidate only if it reproduces on disjoint halves of the same
teams' matches (split-half) or survives a variance decomposition
against its sampling-noise floor. Split-half figures are career-pooled
per team (alternating split, ≥10 matches/team); with 15 teams, an |r|
under ~0.3 has a wide confidence interval and is treated as weak
evidence at best.

## Levels (regular season)

| Quantity (per match) | 2021 | 2022 | 2023 | 2024 | 2025 | Dev pooled | Virgin 2026* |
|---|---|---|---|---|---|---|---|
| Goals | 2.70 | 2.99 | 3.06 | 2.63 | 2.80 | 2.84 | 2.80 |
| Home goals / away goals | 1.44 / 1.26 | 1.42 / 1.58 | 1.62 / 1.44 | 1.47 / 1.16 | 1.56 / 1.25 | 1.51 / 1.33 | 1.62 / 1.18 |
| Home edge (goals) | +0.18 | **−0.16** | +0.18 | +0.31 | +0.31 | +0.18 | +0.44 |
| Home win / draw / away win % | 42.2 / 23.7 / 34.1 | 36.8 / 24.3 / 38.9 | 40.0 / 23.9 / 36.1 | 40.6 / 30.0 / 29.4 | 45.3 / 23.5 / 31.3 | 41.1 / 25.2 / 33.7 | 49.4 / 23.3 / 27.2 |
| BTTS % / Over 2.5 % | 51.1 / 54.8 | 55.6 / 60.4 | 52.8 / 57.8 | 54.4 / 47.8 | 54.2 / 54.2 | 53.8 / 54.8 | 53.3 / 53.9 |
| Red-family events | 0.22 | 0.22 | 0.23 | 0.19 | 0.20 | 0.21 | 0.18 |
| "Yellow" events (YellowRed only) | 0.09 | 0.08 | 0.12 | 0.09 | 0.01 | 0.08 | 0.01 |

\* 2026 shown for the record (coverage inventory); it is virgin for
fitting, feature selection, and gate setting.

Dispersion (variance/mean of the match goal total): 1.06, 0.99, 1.09,
0.89, 0.93 across dev seasons — near-Poisson, the same regime as the
top-5 production markets and the sibling Premier Division.

Context vs references: the First Division scores like the top-5 spine
(2.84 vs 2.84 goals) and more than J1 (2.55) and its own Premier
Division sibling (whose dev goals sit near 2.5–2.7). It is a
second-tier league that out-scores its first tier — the cross-tier
story is in F4, not in the levels.

## Findings

**F1 — League levels are league facts, and they drift by season.**
Goals by season: 2.70, 2.99, 3.06, 2.63, 2.80 (regular). Over-2.5
rate swings 47.8%–60.4%. The home edge is unstable: +0.18, −0.16,
+0.18, +0.31, +0.31 — 2022 is an away-edge season (away goals 1.58
vs home 1.42; away wins 38.9% vs home wins 36.8%), the only such
season in either Irish division's dev window.
Verdict: **SIGNAL** (descriptive fact). Design consequence: per-league
levels with time-decayed fitting, as in production; no cross-league
level borrowing beyond shrinkage priors for thin leagues. A fitted
home advantage that cannot go negative would misprice 2022-style
seasons — the DC fit estimates `h` per window, which is the right
shape here.

**F2 — Core team traits are strongly reliable.**
Career split-half r (15 teams, dev regular): goals-for **0.824**,
goals-against **0.961**. Season-to-season lag correlations of team
goals-for: 2021→2022 r=0.391 (n=7), 2022→2023 r=0.668 (n=8),
2023→2024 r=0.451 (n=8), 2024→2025 r=−0.027 (n=9). The lag series
is noisy — the 2024→2025 negative is carried by churn (Dundalk and
Cork City arriving from the Premier Division as instantly-strong
sides, Waterford leaving) — but the career-pooled split-half is
unambiguous: this league's clubs differ hugely and persistently
(Kerry FC 2023: GF 0.81 / GA 2.53 per match; Cork City 2024:
GF 1.78 / GA 0.64).
Verdict: **SIGNAL-CANDIDATE (strong)** — a ratings architecture has
real, persistent team signal to capture. This is the green light for
the goals candidate. (Caveat recorded: n=15 teams makes the
split-half interval wide; the dev walk-forward gate, not this number,
decides whether the signal is usable.)

**F3 — Half shares are noise here too, for goals.**
True variance of the per-match first-half goal share (observed
variance minus the binomial noise floor): pooled 2021–2025 **0.000**
(n=763 matches with derivable HT; per-season true SD 0.000 except
2022 at 0.090, which is a single-season wobble inside its own noise).
League constant (ratio of sums over dev regular): **1H share of
goals = 0.441** (per-season 0.399–0.460). No team-level split-half
was run — there is no per-half team stat to split, and the variance
decomposition is the sharper instrument; it says zero.
Verdict: **NOISE.** Halves products, if ever built here, use the
frozen league constant 0.441 exactly as production does. This book
stays closed.

**F4 — The cross-tier gap for relegated movers is ≈ +0.23 GF / −0.27 GA,
noisy and asymmetric in the details.**
Six relegated-from-Premier arrivals in dev (2022: Longford Town,
Waterford FC; 2023: Finn Harps; 2024: UCD, Cork City; 2025:
Dundalk), plus one brand-new club (Kerry FC, 2023). Relegated
movers' first-season deltas vs that season's league mean (goals per
team-match): GF +0.03, +0.69, −0.45, −0.01, +0.46, +0.65 (mean
**+0.23**); GA −0.22, −0.43, +0.53, −0.29, −0.68, −0.54 (mean
**−0.27**). Four of six score more, five of six concede less — the
direction is the J1 F4 direction (moving down a tier helps), but the
magnitude is about half J1's ±0.5 and one mover breaks it outright:
Finn Harps arrived relegated *and* weak (GF −0.45, GA +0.53), because
they were relegated for being bad, not unlucky. Kerry FC as a new
club is the mirror image: GF −0.72, GA +1.00 vs league mean — new
clubs start at the bottom, with n=1.
Verdict: **SIGNAL-CANDIDATE (weak, n=6)** — justifies testing a
relegated-mover offset arm (feature X2) through the gate, with the
frozen magnitudes +0.23 / −0.27, not by assumption. The Finn Harps
case is why the arm must be gated, and why no offset is applied to
brand-new clubs (n=1, league mean is the honest prior).

**F5 — The 2022 away-edge season is real in the data, not a
recording artefact.** 2022: home goals 1.42 vs away 1.58, home wins
36.8% vs away wins 38.9%, over 2.5% 60.4% (the dev maximum). It is a
9-team season (one bye per round); nothing in the payloads suggests
a venue or recording cause. Verdict: **descriptive** — recorded so
the walk-forward harness is expected to struggle in 2022 and so
nobody "discovers" a venue effect later without this context. No
design consequence beyond the time-decayed fit (F1).

**F6 — Feasibility boundary (fact).** This league supports a goals
model only. SOT, corners, total shots, and xG have no target in any
season; yellows have no target in any season (Phase 1 §4.1); no
referee is ever named; no per-half stats exist. The virgin window
(2026) contains goals and nothing else. Per the locked design rule,
model scope is set by this matrix — the architecture is shared, the
menu is not.

## What is genuinely new here vs the references

1. A second tier that out-scores its first tier (2.84 vs ~2.5–2.7) —
   the cross-tier bridge runs the other way from J.League's (the
   relegated side is the strong side here, and only mildly so).
2. A negative home-edge season inside the dev window (2022) — the
   production pattern's fitted `h` is load-bearing here in a way it
   is not in most leagues.
3. A negative control for the whole programme: a league where four
   of five candidate markets do not exist at all, so the six-step
   process must produce a documented NOT-buildable verdict, not a
   model.
