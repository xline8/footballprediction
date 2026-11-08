# Phase 3 — EDA: J.League Corpus (J1 / J2 / J3, 2021 – 2026/27)

Computations: `eda.py` (digest in `eda_summary.json`) + `absence_test.py`.
Tables: Phase 2 outputs in `data/`. Sample sizes: J1 2,091 matches,
J2 2,318, J3 1,819; J1 shotmap era 2022+ = 1,711 matches / 43,034
regulation shots (537 shootout attempts excluded, Phase 2 rule 5). Every pattern below carries a verdict under the
halves-audit standard: **a trait is a signal candidate only if it
reproduces on disjoint halves of the same teams' matches (split-half) or
survives a variance decomposition against its sampling-noise floor.**
Split-half figures below are career-pooled per team (≥24 matches/team,
60 random splits averaged, odd/even split included); with 23–36 teams
per trait, an |r| under ~0.3 has a wide confidence interval and is
treated as weak evidence at best.

## Levels (all matches in scope; stats-window caveats as noted)

| Quantity (per match) | J1 | J2 | J3 |
|---|---|---|---|
| Goals | 2.55 (SD 1.65) | 2.48 | 2.57 |
| Home goals / away goals | 1.38 / 1.18 | 1.30 / 1.17 | 1.36 / 1.20 |
| Home win / draw / away win % | 41.3 / 26.8 / 31.9 | 38.2 / 27.7 / 34.2 | 42.6 / 24.2 / 33.2 |
| BTTS % / Over 2.5 % | 50.4 / 47.0 | 50.4 / 45.7 | 51.5 / 47.9 |
| Shots | 24.8 | 24.0 (window n=1,394) | — (62-match window: 25.5) |
| SOT | 8.08 | 7.63 (window) | — (window: 8.27) |
| Corners | 9.47 | 9.55 (window) | — (window: 9.94) |
| Yellow cards | 2.34 | 2.28 (events) | — (window: 2.26) |
| Red cards | 0.11 | 0.09 | 0.08 |
| Team xG (stats feed) | 2.52 | — | — |

Dispersion (variance/mean of the match total): goals 1.05–1.07 in all
three tiers (near-Poisson), SOT 1.19, total shots 1.32–1.35, corners
1.15–1.21, yellows ≈ 1.0–1.09. Mild overdispersion everywhere;
negative-binomial sizes will be large but finite — the same regime as
the top-5 production markets.

Context vs the top-5 spine: J.League scores slightly less (2.55 vs
2.84 goals), shoots slightly less (24.8 vs ~25.6), and is dramatically
more disciplined (2.34 vs 4.04 yellows per match). Any ported model
whose level prior comes from Europe is wrong here by construction —
which is the empirical core of the user's 1-league-1-model decision.

## Findings

**F1 — League levels are league facts, and they drift by season.**
J1 goals by season: 2.42, 2.52, 2.54, 2.67, 2.40, 2.66 (transitional),
2.96 (2026/27 — an Aug–Nov segment only, NOT comparable to full
seasons). J1 shots drift 23.5 → 26.2 → 24.1 across full seasons;
yellows step from 1.78 (2021) to a 2.2–2.8 era. Home edge: J1 +0.20,
J2 +0.13, J3 +0.16 goals, season range in J1 +0.09…+0.27.
Verdict: **SIGNAL** (descriptive fact). Design consequence: per-league
levels with time-decayed fitting, as in production; no cross-league
level borrowing beyond shrinkage priors for thin leagues.

**F2 — Core team traits are strongly reliable in all three tiers.**
Career split-half r (J1 / J2 / J3): shots-for 0.85 / 0.82 / —,
SOT-for 0.76 / 0.80 / —, xG-for 0.77 / — / —, goals-for 0.71 / 0.69 /
0.66, corners-for 0.65 / 0.64 / —, yellows-for 0.66 / 0.51 / —,
goals-against 0.59 / 0.62 / 0.68. Season-to-season lag correlations
0.39–0.58. Verdict: **SIGNAL-CANDIDATE (strong)** — a ratings
architecture has real, persistent team signal to capture everywhere,
including scores-only J3 (goals traits only). This is the green light
for the shared architecture, per league.

**F3 — Half shares are noise in J1 too, for every counting stat.**
True variance of the per-match first-half share (observed variance
minus the binomial noise floor): goals **−0.001**, SOT **+0.00001**,
corners **−0.0006**, shots **−0.0007** — zero or below the floor in all
four. Team-level share split-half r: corners 0.05, xG 0.17, goals 0.19,
shots 0.29, SOT 0.33 (26 teams; the two larger values are ~1.5 SE from
zero and are contradicted by the variance decomposition, the sharper
instrument). League constants (J1): 1H share of goals 0.412, SOT 0.448,
corners 0.447, shots 0.455. Verdict: **NOISE.** The top-5 halves audit
replicates on a second continent and three more stats: no team has a
first-half/second-half tendency worth modelling. Halves products, if
ever built here, use frozen league constants exactly as production
does. This book stays closed.

**F4 — The cross-tier gap is ≈ half a goal per match, symmetric.**
Promoted J2→J1 (n=13 team-seasons): goals-for 1.60 → 1.04 (−0.56),
goals-against 0.91 → 1.41 (+0.51), PPG 1.94 → 1.10. Relegated J1→J2
(n=10): GF 1.02 → 1.50, GA 1.68 → 1.13, PPG 0.89 → 1.65. J3→J2 movers
(n=9 up, 11 down) show the same magnitudes (GF −0.48 up, GA +0.56 up).
Verdict: **SIGNAL.** A promoted champion is, on arrival, a
below-average top-tier side; the mover bridge supports a tier offset
of roughly 0.5 goals/match in each direction when a team's prior must
cross tiers (first-season priors for promoted/relegated teams).

**F5 — Set-play xG share is a stable team identity (NEW).**
Split-half r = **0.621** (J1, ratio of sums). The spine has no set-play
split at all; FotMob's stats feed carries xG open-play / set-play /
non-penalty per match. Verdict: **SIGNAL-CANDIDATE** — justifies
testing an open-play/set-play decomposition of the attack input in
the goals/SOT designs, through the gate, not by assumption.

**F6 — Shot quality is mildly real; shot outcomes are noise.**
J1 split-half r: xG per shot **0.437** (shot selection quality —
mildly stable), goals per shot 0.338 (weak), finishing (goals − xG)
**0.153 → NOISE**, on-target rate (SOT/shots) **0.06 → NOISE**.
Verdict: mixed. Design consequence: an SOT model here should key on
shot volume and xG/shot — the v5 architecture's inputs — and must NOT
chase trailing conversion, finishing, or SOT-rate "form". The same
traps the top-5 autopsy found, confirmed in advance on new data.

**F7 — xGOT: attacking post-shot quality shows stability; defensive
does not (NEW, era-limited).** Mean xGOT per shot (2025+ era, where the
field is populated for ~all shots): split-half r = **0.518** (23
teams) attacking; xGOT-against per shot r = **0.116 → NOISE**.
Verdict: **SIGNAL-CANDIDATE with two caveats** — the era is short
(2025 + transitional 2026 + partial 2026/27, min 20 matches/team) and
23 teams make the interval wide; and the population rule differs
before 2025, so the trait is not measurable on the full history.
Any use must be gated on the recent era only.

**F8 — Referee strictness is a real trait (NEW).** Cards per match by
referee (event feeds, all tiers pooled): split-half r = **0.646**
(20 referees with ≥20 matches; 87 referees seen; attendance present
for 2,234 matches). Caveat: J3 event feeds omit yellows, so J3-heavy
referees are biased low in the pooled check — the J1/J2-only trait is
at least this strong. The production cards model does not use the
referee. Verdict: **SIGNAL-CANDIDATE** for a J.League cards design,
subject to a walk-forward gate and to referee assignment being known
pre-match at prediction time (an operational check, not a data one).
Recheck for the feature step (J1+J2 only, yellows only, same helper):
r = **0.649**, 20 referees — the pooled figure is not a J3 artefact.

**F9 — Territorial pressure: box touches are the corners proxy
(PRODUCTION FINDING REPLICATES, STRONGER).** Team opp-box-touches
trait split-half r = **0.857** — the most stable team trait measured
in this EDA. Per team-match, corners correlate 0.471 with own box
touches vs 0.286 with possession (n=3,202). Verdict:
**SIGNAL-CANDIDATE** — pre-match team box-touch rates are a legitimate
candidate input to a corners design here, the direct analogue of
production's territorial multiplier (which used possession/big
chances because the spine had nothing better). Companion measures
taken for the feature step: box touches *conceded* are also a stable
team trait (split-half r = **0.687**), and production's own big-chance
covariate is reliable here too (r = **0.738**) — so the gated
comparison is box touches vs a genuinely strong reference arm, not
against a straw man.

**F10 — Star absence: the V10 null replicates (CLOSED STAYS CLOSED).**
V10's protocol on J1 2022+ (star = ≥25% of team SOT over trailing 10,
absent = not in matchday squad): n=107 absences, mean SOT residual
**+0.04** (95% CI −0.34…+0.41) vs control +0.04; dose split gives
opposite signs (≥30% share: −0.25; 25–30%: +0.21), both null.
Verdict: **NOISE — no new evidence.** Lineup/absence features remain
forbidden; this is recorded as a replication, not a reopening.

**F11 — FotMob xG is calibrated for J1.** Goals per unit xG by season
(stats feed): 1.080 (2022), 0.984, 1.033, 0.980, 1.025, 1.093
(partial) — pooled 2022–2025 ≈ 1.02, no systematic bias, ±8% seasonal
wobble. Verdict: **SIGNAL** (input quality fact). The production
blend idea (fit on goals + xG) has a sound input here.

**F12 — Timing and game state (descriptive only).** Goals by 15-min
block (all tiers, 15,749 event goals): 1,862 / 2,100 / 2,173 / 3,052 /
2,556 / 4,006 — **24.2% of goals arrive at 76'+**, and J1's 1H goal
share (0.412) is lower than the top-5's 0.442: Japan scores late.
Scoring first is worth 2.31 PPG (home first) / 2.13 PPG (away first)
in J1. These are in-match facts, NOT pre-match features; no signal
claim is made for prediction. Recorded so nobody "discovers" them
later as features without a reliability check.

**F13 — Feasibility boundary by tier (fact).** J3 supports a goals
model only: no SOT/shots/corners/cards targets exist (outside the
62-match 2025 window), HT is missing for 6.8% of matches. J2 supports
goals everywhere; SOT/shots/corners only inside the Sep 2021–Sep 2024
stats window (1,394 matches); cards from events everywhere; no xG, no
per-half stats, no shotmap. J1 supports everything from 2022, with
per-half stats complete only from 2024 (86% in 2023). Per the locked
design rule, model scope is set per league by this matrix — the
architecture is shared, the menu is not.

**F14 — Yellow-card half share: the F3 constant for cards (measured
2026-11-09, `cards_halves.py`).** Source: Phase 2 match table,
stats-feed period splits (`has_stats_half == True`: 1,362 matches;
analysis set = 1,263 matches with FT yellows > 0, 3,440 yellows).
The pooled first-half share over all flagged rows is 0.357, but the
2023 splits are artefact-suspect: their 1H share is **0.263** against
**0.336** from the event feed on the same matches, while in every
complete-era season the two instruments agree to ≤0.003 (2024: 0.395
vs 0.393; 2025: 0.369 vs 0.368; 2026: 0.368 vs 0.365; 2026/27: 0.401
vs 0.401). The constant is therefore taken from the complete era
only (per-half stats complete from 2024, F13): **frozen J1 1H yellow
share = 0.383** (ratio of sums; n = 1,016 matches, 2,707 yellows;
event-feed cross-check on the same matches: 0.381). Variance
decomposition, same instrument as F3: the two full normal seasons
sit at or below the binomial noise floor (**2024: −0.00094; 2025:
−0.00028**); pooled 2024+ excess is +0.00403, carried by the two
small-n seasons (transitional 2026, n=182: +0.01792; partial
2026/27, n=133: +0.00922 — each within ~1.4 SE of zero for a
variance estimate at that n) and by between-season drift of the
constant itself; the all-rows pooled excess (+0.00690) is further
inflated by mixing in the biased 2023 splits. Team-level 1H yellow
share split-half r = **0.097** (26 teams) — no team tendency.
Verdict: **NOISE — constant adopted.** Cards halves join F3's four
stats under the frozen-constant mechanism: J1 yellows split
**0.383 / 0.617**. This book stays closed.

## What is genuinely new here vs the master spine

1. Per-shot xG **and xGOT** with situation/location (J1 2022+) —
   enables shot-quality traits (F6, F7) the spine cannot express.
2. Set-play / open-play xG splits (F5) — a stable team identity with
   no spine analogue.
3. Referee identity per match (F8) — a validated cards input the
   production cards model never had.
4. Opp-box touches (F9) — a stronger territorial trait than the
   possession/big-chance proxies production was limited to.
5. A measured cross-tier bridge (F4) — the spine is single-country
   top-5 with no promotion bridge into a second tier of the same
   system at this depth (J2 and J3 are full leagues, not samples).
6. Negative knowledge, replicated: half shares (F3), finishing and
   SOT-rate as team traits (F6), star absence (F10) — three tempting
   feature families killed on new data before any model was built.
   That is the EDA doing its job.
