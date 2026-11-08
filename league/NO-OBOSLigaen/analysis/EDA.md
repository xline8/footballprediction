# Phase 3 — EDA: Norway OBOS-ligaen (2021 – 2026)

Computations: `eda.py` (digest in `eda_summary.json`; coordinator
recomputed the levels, primary lines and mover counts independently
from the CSV — all agree). Sample: 1,440 matches, 32 distinct clubs
(16 per season). Standard, as in J1/NO-Eliteserien: **a trait is a
signal candidate only if it reproduces on disjoint halves of the same
teams' matches (split-half, career-pooled, ≥24 team-matches, 30 seeded
splits) or survives a variance decomposition against its sampling-noise
floor.** With 32 clubs the practical noise-zone line is |r| ≈ 0.3.

## Levels

| Quantity (per match) | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 (virgin) | Pooled | NO-Eliteserien | J1 |
|---|---|---|---|---|---|---|---|---|---|
| Goals | 3.19 | 3.29 | 2.78 | 3.19 | 3.20 | **3.79** | 3.24 | 3.12 | 2.55 |
| Home / away goals | 1.78/1.40 | 1.78/1.51 | 1.55/1.23 | 1.73/1.46 | 1.66/1.54 | 2.15/1.63 | 1.78/1.46 | 1.77/1.35 | 1.38/1.18 |
| Home win % | 47.1 | 43.8 | 45.4 | 42.1 | 40.4 | 50.8 | 44.9 | 46.9 | 41.3 |
| Total shots | 18.0* | 18.4 | 19.2 | 23.9 | 21.4 | 23.3 | 20.9 | 26.7 | 24.8 |
| SOT | 8.80* | 9.48 | 7.40 | 11.85 | 10.64 | 9.77 | 9.72 | 9.14 | 8.08 |
| Corners | 10.06* | 10.85 | 10.50 | 11.05 | 10.47 | 11.07 | 10.71 | 10.62 | 9.47 |
| Yellow cards (events) | 3.14 | 2.93 | 3.13 | 3.24 | 3.36 | 3.35 | 3.19 | 3.26 | 2.34 |

*2021 stats levels cover only the 136 matches with the stats keys
(rounds ~14–30); they are not full-season levels.

OBOS scores like its parent tier (3.24 goals pooled vs Eliteserien
3.12) with a slightly smaller home edge (+0.32 vs +0.42). The counting
stats are NOT comparable to the parent's at face value: the OBOS stats
feed counts fewer shots (20.9 vs 26.7) — a feed-definition difference
compounded by the 2024 regime jump (F9) — so cross-tier level
comparisons for shots/SOT are descriptive only. The virgin season
2026 ran very hot on goals (3.79 vs dev 3.11) — the hottest season in
the corpus by a wide margin; the gates, not the means, will judge
what that does to the goals model.

Dispersion (variance/mean of match total, pooled): goals 0.98,
SOT 1.92, corners 1.16, total shots 2.03, yellows 0.90. SOT and total
shots are far more overdispersed than in NO-Eliteserien (1.21 / 1.54)
— partly the regime mixture (F9) — which is the E9 trailing-r
mechanism's home ground and a headwind for the v5 SOT pattern's frozen
NB size.

## Findings

**F1 — League levels drift by season.** Goals 2.78–3.29 across the
complete dev seasons, then 3.79 in the virgin; corners stable
10.5–11.1; event yellows 2.93–3.36 with no trend. Home edge +0.32
goals pooled, home-win rate 40.4–50.8% by season. Verdict: **SIGNAL**
(descriptive fact) — per-league fitting with time decay, as in
production.

**F2 — Core team traits are strongly reliable.** Career split-half r:
shots-for 0.895, SOT-for 0.858, goals-for 0.825, goals-against 0.727,
corners-for 0.730, shots-against 0.758, SOT-against 0.672,
corners-against 0.525, yellows-for 0.408, yellows-against 0.382.
Verdict: **SIGNAL-CANDIDATE (strong)** — a ratings architecture has
real signal in every market, cards included (weakest, as everywhere).

**F3 — Half shares are noise; two markets have a halves source at
all.** True variance of the per-match 1H share (observed minus
binomial floor): goals **−0.0067**, cards **+0.0039**. Only goals and
cards have any 1H source (event times — the stats feed has no period
splits); SOT, corners and total shots have none. League constants
(ratio of sums, all seasons): goals **0.440**, cards **0.306**.
Verdict: **NOISE** for both measured markets — halves are frozen-
constant presentation only, exactly as production; SOT/corners/shots
are FT-only (RU-1Division precedent).

**F4 — Mover effect is REAL and large (X2 measurable here).** The
parent tier's corpus exists, so entrants relegated from Eliteserien
are identifiable by team id. Entrants per season 2022–2026: 5, 4, 6,
4, 5 — of which from Eliteserien 3, 2, 3, 2, 3 (13 entrant-seasons)
and from 2. divisjon 2, 2, 3, 2, 2 (no parent corpus — count only).
Pooled Eliteserien entrants in their entry season: **GF 2.053, GA
1.348 per match vs the league team-goal mean of 1.619** — they attack
+0.43 above the league mean and concede −0.27 below it. Relegated
clubs are simply much stronger than the OBOS field. Verdict:
**SIGNAL** — justifies the pre-registered X2 mover-offset arm for the
goals candidate, scoped to Eliteserien entrants only; entrants from
below have no measurable offset and take the league-mean prior (the
SHR arm covers their thin-history problem).

**F5 — Set-play / shot-quality family: NOT MEASURABLE.** There is no
xG of any kind and no shotmap in this feed, so X3, X4 and X6 have no
inputs. Verdict: **DATA ABSENT** — dropped at the feature step, never
faked.

**F6 — Shot outcomes family: NOT MEASURABLE as covariates.**
Finishing, conversion and on-target rate as trailing covariates need
shot-level or xG data; the four-key stats feed carries only team
totals. The on-target ratio inside the v5 SOT architecture is a
fitted component (§2 of FEATURES.md), not a covariate, and remains
available to Gate Zero. Verdict: **DATA ABSENT** for the covariate
forms.

**F7 — xGOT: NOT MEASURABLE** (no shotmap in any season). Dropped
with X6.

**F8 — Referee strictness is a strong trait here.** Cards per match
by referee (19 referees with ≥20 matches, 1,181 matches with a named
referee; 2022+ only — 2021 names nobody): split-half r = **0.715**,
independently recomputed on a second seed stream at **0.723**. That
is the strongest referee reading in the program (J1 0.646,
NO-Eliteserien 0.316). Coverage: 95.4% of 2022–2026 matches, 95.4% in
the virgin season (229/240). Verdict: **SIGNAL-CANDIDATE (strong)** —
justifies the gated X8 arm, subject to the pre-match-availability
fallback as in K-J1/K-NO.

**F9 — The stats feed changed counting regime in 2024.** SOT by
season: 8.80*, 9.48, 7.40, **11.85**, 10.64, 9.77; total shots: 18.0*,
18.4, 19.2, **23.9**, 21.4, 23.3. A jump of +4.5 SOT and +4.7 shots
per match between 2023 and 2024 with no corresponding goals/corners
move is a feed/counting change, not football. Consequences, recorded
not corrected: the dev window spans both regimes, so SOT/total-shots
ratings fitted across the break carry a level mixture; the virgin
(2026) sits in the new regime. The gates judge the result as built.

**F10 — Star absence: not re-run; the question stays closed.** The
V10 protocol produced a null on the top-5 and replicated nulls since;
no new reliability evidence exists in this corpus (no shotmap, no
player data usable pre-match). Lineup/absence features remain
forbidden.

**F11 — xG calibration: NOT MEASURABLE** (no xG). The goals model is
goals-only throughout (the production blend's documented fallback is
the whole design here, as in J2/J3).

**F12 — Feasibility boundary (fact).** All five markets are buildable:
goals/SOT/corners/cards/total-shots targets exist in the dev seasons
and in the virgin season (count targets missing only where the stats
keys are missing: 1 match in 2025, 3 in 2026 — those rows are skipped
by count-market scoring, never imputed). The constraints are
feature-side only: no xG/shotmap/touches/big-chances anywhere, period
splits nowhere, referee names absent in 2021 (warm-up only), and the
2024 counting-regime break (F9).
