# Step 3 — EDA: Algeria Ligue 1 (FotMob 516)

Computations: `analysis/eda_numbers.py` (digest in
`analysis/eda_numbers.json`). Tables: step-2 outputs in `data/`.
Sample size: 1,332 matches (1,331 eligible; the awarded match
4366461 is excluded from every number below). Every pattern carries
a verdict under the halves-audit standard: **a trait is a signal
candidate only if it reproduces on disjoint halves of the same
teams' matches (split-half) or survives a variance decomposition
against its sampling-noise floor.** Split-half figures below are
career-pooled per team-season (≥10 matches/team, ≥5 per half); with
16–18 teams per trait, an |r| under ~0.3 has a wide confidence
interval and is treated as weak evidence at best.

## Levels (eligible matches only; 2026/2027 partial, not comparable)

| Quantity (per match) | 2021/2022 | 2022/2023 | 2023/2024 | 2024/2025 | 2025/2026 (virgin) | Pooled completed |
|---|---:|---:|---:|---:|---:|---:|
| n (eligible) | 306 | 240 | 239 | 240 | 240 | 1,265 |
| Goals | 2.26 | 2.15 | 2.31 | 1.95 | 2.27 | **2.19** |
| Home goals / away goals | 1.38 / 0.89 | 1.43 / 0.72 | 1.40 / 0.92 | 1.19 / 0.75 | 1.35 / 0.91 | **1.35 / 0.84** |
| Home edge (goals) | +0.49 | +0.71 | +0.48 | +0.44 | +0.44 | **+0.51** |
| Home win / draw / away win % | 48.0 / 28.1 / 23.9 | 57.1 / 26.7 / 16.3 | 51.5 / 25.5 / 23.0 | 48.3 / 31.3 / 20.4 | 50.0 / 29.2 / 20.8 | **50.8 / 28.1 / 21.0** |
| BTTS % / Over 2.5 % | 39.9 / 37.6 | 40.0 / 37.5 | 44.8 / 41.4 | 39.6 / 34.6 | 48.8 / 39.2 | **42.5 / 38.0** |
| 0-0 % | 14.1 | 12.9 | 11.7 | 17.5 | 8.3 | 13.0 |
| Goals dispersion (var/mean) | 1.41 | 1.00 | 1.26 | 1.05 | 1.01 | 1.17 |

Context vs the J.League/Europe reference points: Algeria scores
far less (2.19 vs J1 2.55, top-5 2.84) and is far more home-tilted
(home edge +0.51 vs J1 +0.20; home wins 50.8% vs J1 41.3%, away
wins only 21.0% vs 31.9%). Over 2.5 sits at 38.0% (J1 47.0%).
Any ported model whose level prior comes from Europe is wrong here
by construction — which is the empirical core of the user's
1-league-1-model decision. Dispersion 1.17 pooled (per-season
1.00–1.41) is mild overdispersion; a Poisson-family DC fit is in
the same regime as the top-5 production markets.

## Findings

**F1 — League levels are league facts, and they drift by season.**
Goals by season: 2.26, 2.15, 2.31, **1.95** (2024/2025 — the low
outlier; home goals fall to 1.19 and 0-0s rise to 17.5%), 2.27
(2025/2026 virgin). Home edge stays +0.44…+0.71 every season — the
home tilt is structural, not a one-season artefact. Home-win rate
peaks at 57.1% in 2022/2023. Verdict: **SIGNAL** (descriptive
fact). Design consequence: per-league levels with time-decayed
fitting, as in production; no cross-league level borrowing beyond
shrinkage priors for thin teams.

**F2 — Team traits are moderately reliable — with a split by era.**
Career-pooled split-half r (82 team-seasons): goals-for **0.396**,
goals-against **0.602**. Per season: attack 0.35, 0.29, 0.29, 0.54,
0.64 (rising in the later seasons); defence 0.74, 0.78, 0.77, 0.15,
0.03. The pooled defence figure is carried entirely by the first
three seasons — in 2024/2025 and 2025/2026 the defensive trait
vanishes (r ≈ 0.15, 0.03). Honest reading: attack is a moderate,
strengthening trait; defence was a strong trait that has not
reproduced in the last two seasons. Whether the DC ratings add
signal is exactly what the dev gate adjudicates — no trait claim
beyond these numbers is made. Verdict: **SIGNAL-CANDIDATE
(moderate, era-qualified)** — a ratings architecture has real team
signal to work with, but less than the pooled defence number alone
suggests.

**F3 — Half shares are noise, for goals (the only measurable stat).**
Frozen goals 1H share = **0.4421** (ratio of sums over completed
seasons; 1,226 HT goals / 2,773 FT goals, n = 1,129 HT-readable
matches). True variance of the per-match first-half share
(observed variance minus the binomial noise floor): pooled
**−0.00039** — at/below the floor. Per-season excess: +0.0040,
−0.0008, −0.0030, −0.0082, +0.0030 — no season shows a real excess.
Team-season 1H-share split-half r = **−0.05** (82 pairs). Verdict:
**NOISE.** No team has a first-half tendency worth modelling.
Halves presentation, if ever wanted, uses the frozen league
constant exactly as production does. This book stays closed. (Note:
0.4421 is essentially the top-5's frozen 0.4419 — the same
constant, arrived at independently on a different continent.)

**F4 — Cross-tier gap: unmeasurable here (no sibling league).**
Two promoted clubs enter every season (DATA_UNDERSTANDING §3) and
the league shrank 18 → 16 after 2021/2022, but no other Algerian
league exists in the warehouse, so no mover transition is
observable and no tier-step offset is estimable. The SHRINK arm
(MODEL_DESIGN §2) is the thin-data treatment, motivated by the
G-J2 post-mortem, not by a measured offset. Verdict: **NO
EVIDENCE** — X2 is dropped, not estimated.

**F5 — Set-play xG share: NO EVIDENCE** — no xG splits exist
(stats empty in 1,332/1,332 payloads). Not measurable, not used.

**F6 — Shot quality / finishing / on-target rate: NO EVIDENCE** —
no shotmap, no shot counts, no xG exist. Nothing in this family can
be reliability-tested here; none of it enters any design.

**F7 — xGOT: NO EVIDENCE** — no shotmap exists. Not measurable.

**F8 — Referee strictness: NO EVIDENCE** — referee text is empty
in 1,332/1,332 payloads and no yellow target exists. Not measurable.

**F9 — Territorial pressure (box touches): NO EVIDENCE** —
`touches_opp_box` exists in 0/1,332 payloads. Not measurable; the
corners candidate does not exist here in any case.

**F10 — Star absence: CANNOT TEST, CLOSED ANYWAY.** No lineups
(1 match in 1,332 has starters) and no player stats exist, so the
V10 protocol cannot run here. The production V10 null stands
unreplicated but unchallenged; lineup/absence features remain
forbidden.

**F11 — FotMob xG calibration: NOT APPLICABLE** — no xG exists.
The goals model is goals-only by necessity (the reference blend's
documented fallback).

**F12 — Timing (descriptive only).** 132 goals at minute 45
(first-half stoppage time, correctly counted in HT by the Half
event — see DATA_UNDERSTANDING §2). No signal claim is made for
prediction. Recorded so nobody "discovers" minute-45 goals later
as a feature without a reliability check.

**F13 — Feasibility boundary (fact).** Algeria Ligue 1 supports a
goals model only: no SOT/shots/corners/cards targets exist in any
season (outside nothing — there is no stats window at all, unlike
J2's windowed corpus), HT exists for 89.3% of matches, lineups
effectively do not exist. Per the locked design rule, model scope
is set per league by this matrix — the architecture is shared,
the menu is not.

## What is genuinely new here vs the master spine

1. The strongest home edge in the program so far (+0.51 goals,
   50.8% home wins) paired with the lowest scoring level (2.19) —
   a combination no European prior would produce.
2. A defence trait that was strong for three seasons and then
   vanished (r 0.77 → 0.03) — a live warning that pooled
   reliability can be an era artefact, and a case the dev gate
   (not the EDA) must adjudicate.
3. Negative knowledge, confirmed again: half shares (F3) are noise
   on a third continent; and the scores-only shape means five of
   the J1 feature families (F5–F9) are not even testable here —
   the EDA's job in this league is mostly to say what does not
   exist, precisely.
