# Phase 3 — EDA: Norway Eliteserien (2021 – 2026)

Computations: `eda.py` (digest in `eda_summary.json`). Sample: 1,407
matches, 23 clubs. Standard, as in J1: **a trait is a signal candidate
only if it reproduces on disjoint halves of the same teams' matches
(split-half, career-pooled, ≥24 team-matches, 30 seeded splits) or
survives a variance decomposition against its sampling-noise floor.**
With 23 clubs, an |r| under ~0.3 has a wide interval and is treated as
weak evidence at best — the same practical bar as AT.

## Levels

| Quantity (per match) | NO-Eliteserien | AT-Bundesliga | J1 | Top-5 spine |
|---|---|---|---|---|
| Goals | 3.12 (SD 1.75) | 2.81 | 2.55 | 2.84 |
| Home / away goals | 1.77 / 1.35 | 1.52 / 1.29 | 1.38 / 1.18 | — |
| Home win / draw / away win % | 46.9 / 22.6 / 30.5 | 39.5 / 27.5 / 33.0 | 41.3 / 26.8 / 31.9 | — |
| BTTS % / Over 2.5 % | 58.3 / 61.4 | 56.6 / 53.3 | 50.4 / 47.0 | — |
| Total shots | 26.68 | 24.9 | 24.8 | ~25.6 |
| SOT | 9.14 | 8.52 | 8.08 | — |
| Corners | 10.62 | 9.76 | 9.47 | — |
| Yellow cards | 3.26 | 4.07 | 2.34 | 4.04 |
| Red cards | 0.127 | 0.235 | 0.11 | — |
| Team xG (stats feed) | 3.00 | 2.89 | 2.52 | — |

Norway is the **highest-scoring league in the conveyor so far**:
3.12 goals/match, above the top-5 spine (2.84), with the program's
strongest home edge (+0.42 goals; home teams win 46.9%). Counting
stats run high across the board (shots 26.7, corners 10.6, SOT 9.1)
while discipline is mild (3.26 yellows on the event-unified target — between J1's 2.34 and AT's
4.07; the stats feed's 3.09 is an undercount, Phase 1 §3.5). The virgin season (2025) sat close to dev levels on every
counting stat (goals 3.18 vs dev 3.06; SOT 9.28 vs 8.98; corners
10.68 vs 10.55) — unlike AT's cold virgin, no level shift is visible
in the raw means here; the gates will judge the models, not the means.

Dispersion (variance/mean of match total): goals 0.98, SOT 1.21,
corners 1.36, shots 1.54, yellows 0.99. The count markets are notably
**more overdispersed than AT's** (SOT 1.02, corners 1.10, shots 1.24
there) — total shots especially, which is the E9 trailing-r
mechanism's home ground.

## Findings

**F1 — League levels drift by season.** Goals by season: 3.05, 3.25,
3.12, 2.84, 3.18 (complete seasons); SOT 8.99 → 9.28 with a 2024 dip
(8.55); corners stable 10.37–10.88; yellows (event target) 2.91–3.39 with no trend.
Home edge +0.42 goals pooled, home-win rate 41.7–50.8% by season.
Verdict: **SIGNAL** (descriptive fact) — per-league levels with
time-decayed fitting, as in production.

**F2 — Core team traits are strongly reliable.** Career split-half r:
xG-for 0.878, shots-for 0.844, corners-for 0.832, goals-for 0.830,
goals-against 0.636, SOT-for 0.759, yellows-for 0.423 (event target;
0.401 on the defective stats feed). Verdict:
**SIGNAL-CANDIDATE (strong)** — a ratings architecture has real signal
in every market here, cards included (weakest, as everywhere).

**F3 — Half shares are noise here too, with one recorded exception.**
True variance of the per-match 1H share (observed minus binomial
floor), complete-split era 2023–2025: goals −0.0043, SOT −0.0004,
corners +0.0007, shots +0.0006, **yellows +0.0076**. Team-level 1H
goal-share split-half r = −0.089. League constants (ratio of sums,
same era): goals 0.439, SOT 0.456, corners 0.473, shots 0.465,
yellows 0.317. Verdict: **NOISE** for goals/SOT/corners/shots — the
halves book stays closed on a fourth corpus. Yellows are the first
stat in the program with a clearly above-floor half-share variance;
it is recorded as a watch item only — it does not license per-match
or per-team half modelling (the template forbids it, and a share SD
of ~0.09 around a 0.317 constant changes no presentation decision).
Halves products use the frozen constants above, exactly as production
does.

**F4 — No cross-tier bridge is measurable in this build.** Mover
clubs arrive from the 1. divisjon, which has no warehouse build in
this league's scope, so no mover offset can be estimated honestly.
Consequence (design-level): promoted/thin-data teams are handled by
the goals candidate's pre-registered **shrinkage arm** (the template's
sanctioned response to the G-J2 lesson), not by an X2 analogue.
Verdict: **DATA ABSENT** — recorded, not worked around.

**F5 — Set-play xG share is a stable team identity.** Split-half
r = **0.577** (23 clubs). Verdict: **SIGNAL-CANDIDATE** — justifies the
goals decomposition-tilt arm, gated, as in J1.

**F6 — Shot quality is strongly real; shot outcomes are weaker than
in any prior league but stay rejected on the template's terms.**
Split-half r: xG per shot **0.770** (the strongest X4 measurement in
the program; J1 0.437, AT 0.480), on-target rate **0.477** (NOISE in
J1 at 0.06 and AT at −0.114 — a genuine league difference, recorded
in FEATURES §2: the trait is consumed through v5's fitted
Beta-Binomial ratio component, and the RS arm is the gate's test of
how much ratio variation to keep), goals per shot 0.473 (weak and
outcome-contaminated), finishing (goals − xG) **0.312** (above J1/AT's
noise readings but still the weakest of the shot family and
outcome-contaminated by construction). Verdicts: X4
**SIGNAL-CANDIDATE (strong)**; finishing and conversion stay
**REJECTED** — dominated by X4 + volume, and a trait that prices in
the same finishing luck it tries to predict is not a covariate.

**F7 — xGOT attacking trait is reliable where it can be measured,
but its era starts in the virgin season — DROPPED for this build.**
Era-guarded (2025+, where the field is populated for ~99.5% of
shots): split-half r = **0.546**, 19 clubs. That is a real trait
reading, comparable to J1's 0.518. But the fully-populated era begins
with season 2025, which **is** this build's virgin window: no dev
season (2022–2024) carries the field in its guarded form (2024 is a
65.8% transitional mix, a different quantity), so an X6 arm could
never be dev-tested — it could only be read on the virgin, which the
gate discipline forbids. This is the BR-SerieA X6 situation exactly.
Verdict: **DROPPED at the feature step (era/dev mismatch)** — S-NO
has no xGOT arm. A future prereg with 2025 in dev could test it.

**F8 — Referee strictness is a real but modest trait — and the
measurement depends on fixing the cards target first.** Cards per
match by referee (20 referees with ≥20 matches, 1,350 matches with a
named referee): split-half r = **0.291 on the defective stats feed**
(below the 0.3 noise-zone line) but **0.316 on the corrected
event-unified target** (canonical EDA stream; an independent
recompute on a second seeded stream gives 0.348 — both event-target
readings sit above the line, both stats readings below it). Coverage
is not a constraint (95.9% overall, 100% in the virgin season).
Verdict: **SIGNAL-CANDIDATE (modest)** on the corrected target —
justifies the gated X8 referee arm, as in J1, subject to the
walk-forward gate and the pre-match availability fallback. The
feature step's first pass dropped X8 on the stats-feed reading; the
amendment is recorded in FEATURES and PREREG_K_NO. Either way the
trait here is far weaker than J1's 0.646 / AT's 0.547 — expectations
for the arm should be set accordingly.

**F9 — Territorial pressure: box touches are the corners proxy, and
the strongest trait in this EDA.** Team opp-box-touches split-half
r = **0.935** (for) / 0.766 (against) — matching J1's 0.857 and AT's
0.945 class. Per team-match, corners correlate 0.600 with own box
touches vs 0.449 with possession (n=1,958). Production's own
big-chance covariate is also reliable (r = 0.812), so the gated
comparison is box touches vs a genuinely strong reference arm.
Coverage caveat: box touches are complete only from 2024 (38–43%
before) — the arm inherits a minimum-sample rule and falls back to
Gate Zero where its trailing window is thin. Verdict:
**SIGNAL-CANDIDATE**.

**F10 — Star absence: not re-run; the question stays closed.** The
V10 protocol produced a null on the top-5 and a replicated null on J1
(F10 there); the agreed reopening standard (new reliability evidence)
is not met by anything in this EDA. Lineup/absence features remain
forbidden; no arm uses lineups.

**F11 — FotMob xG is calibrated for Norway except for the 2022 feed.**
Goals per unit xG by season: 1.033, **1.216**, 1.053, 0.984, 1.029
(complete seasons) — pooled 1.068. Four of five seasons sit within
±5%; 2022's xG feed undervalues goals by ~20% (Phase 1 §3.2).
Verdict: **SIGNAL with a recorded caveat** (input quality fact) —
the production blend idea has a sound input here overall; G-NO's
2022 dev season is read with the caveat attached, not corrected
post-hoc.

**F12 — Feasibility boundary (fact).** Every market is buildable:
goals/SOT/corners/cards/total-shots targets exist for 100% of matches
in both the dev seasons and the virgin season. The constraints are
feature-side only: period splits before 2023 (halves constants
therefore measured on the complete era, F3), box touches before 2024
(F9 caveat), xGOT era (F7), referee names in 2021
(76.3% — that season is warm-up only in every count market anyway).
