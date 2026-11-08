# Phase 3 — EDA: India Indian Super League (2021/2022 – 2026/2027)

Computations on `data/in_matches.csv` (n=653; 17 teams ever;
split-half checks are career-pooled per team, ≥24 matches/team,
60 random splits averaged — with only 13–15 teams, |r| under ~0.3
has a wide interval and is treated as weak at best, the same
standard as J1/DK/AU). Virgin-window discipline: design-level
aggregates only; no fitting touched 2025/2026.

## Levels

| Season | Goals | SOT | Corners | Yellows (events) | Shots | xG |
|---|---|---|---|---|---|---|
| 2021/2022 | 3.08 | 8.37 | 9.72 | 3.47 | 26.24 | 2.51 |
| 2022/2023 | 2.95 | 8.68 | 10.22 | 3.57 | 26.13 | 2.49 |
| 2023/2024 | 2.77 | 8.24 | 9.87 | 4.61 | 25.86 | 2.41 |
| 2024/2025 | 2.87 | 8.57 | 10.19 | 4.34 | 27.25 | 2.39 |
| 2025/2026 (virgin) | 2.43 | 7.79 | 10.53 | 3.96 | 24.45 | 2.09 |
| 2026/2027 (partial) | 2.93 | 9.96 | 9.86 | 3.29 | 29.50 | 2.70 |
| **Pooled** | **2.84** | **8.44** | **10.08** | **4.02** | **26.28** | **2.40** |

Home/away goals 1.49/1.35 (home edge **+0.14** — the weakest in
the conveyor; the 2021/2022 Goa bubble is part of the story);
HW/D/AW 43.0/24.3/32.6%; Over 2.5 = 54.4%, BTTS = 55.6%.
Dispersion (var/mean): goals 1.04, SOT 1.14, corners 1.23,
yellows 1.03, shots 1.35.

Context: IN sits mid-program on levels — goals 2.84 = the top-5
reference exactly (J1 2.55, DK 2.90, AU 3.07); SOT 8.44 (J1 8.08,
DK 9.22); corners 10.08 (DK 9.98, J1 9.47, AU 10.72); shots 26.28
(DK 26.02); event yellows 4.02 ≈ the top-5's 4.04. Levels are
league facts; the 1-league-1-model rule stands.

## Findings

**F1 — Levels drift, and the virgin ran COLD on attack.** Goals
step down 3.08 → 2.77 by 2023/2024, partly recover, then the
virgin posts 2.43 — the coldest season in the corpus — with SOT
7.79 and shots 24.45 also at corpus lows, while its corners
(10.53) are the corpus *high*. Yellows step UP in 2023/2024
(3.57 → 4.61 events) in both feeds — a real level shift, not the
feed artefact of Phase 1 §3. Verdict: **SIGNAL** (descriptive).
Per-league, time-decayed fitting as in production. The cold
virgin will stress every calibration leg; that is the gate
working as designed, recorded in advance.

**F2 — Core team traits are reliable despite squad churn.** The
brief's worry — foreign-quota/marquee churn making traits
unstable — was measured, not assumed. Career split-half r:
SOT-for **0.820**, shots-for 0.794, goals-for 0.736, xG-for
0.732, corners-for 0.681, goals-against 0.650, yellows-for
0.469 (moderate). Franchise churn does NOT dissolve team
identity here (a closed league of persistent franchises behaves
more like AU/MLS than an open pyramid). Verdict: **SIGNAL** for
the goals/SOT/corners/shots ratings architectures; cards rest
on a moderate trait — noted against K-IN.

**F3 — Half shares are noise, again.** True variance of the
per-match 1H share (observed − binomial floor at the pooled
share), complete-splits dev era (2023/2024–2024/2025, n=302):
goals +0.006, SOT +0.002, corners −0.001, shots +0.001,
yellows −0.002 — zero or a rounding distance from it. **Frozen
IN constants (same era, ratio of sums; goals and yellows from
events): goals 0.435, SOT 0.453, corners 0.458, total shots
0.447, yellows 0.366.** Verdict: **NOISE — constants adopted.**
(2021/2022–2022/2023 splits are too sparse to measure on;
constants come from the dev era only, so the virgin is not used
even at design level for splits.)

**F4 — No relegation, no tier bridge; the thin-data problem is
expansion + the truncated virgin.** No feeder tier exists in the
corpus, so no X2 offset can exist. Newcomers: Punjab FC
(2023/2024), Mohammedan SC (2024/2025) — and, critically, Inter
Kashi and SC Delhi debut **inside the virgin season** with zero
in-league matches, the G-J2 failure mode (extreme lambdas for
1–2-match teams) in its purest form. The sanctioned response is
a pre-registered SHRINK arm in the goals candidate.

**F5 — Set-play xG share is a real team identity.** Split-half
r = **0.489** (ratio of sums, stats-feed splits, all seasons;
J1: 0.621, DK: 0.567, AU: 0.724 — weakest of the four, still
clearly signal). Verdict: **SIGNAL-CANDIDATE** — justifies the
X3 decomposition arm in G-IN, gated against Gate Zero.

**F6 — Shot quality is real; two J1 "noise" verdicts do NOT
replicate here and are recorded honestly.** xG/shot split-half
r = **0.514** (J1: 0.437, DK: 0.348, AU: 0.576) — SIGNAL-
CANDIDATE, X4 arm adopted. On-target rate r = 0.452 and
finishing (goals − xG) r = 0.464 are NOT noise in IN (J1: 0.06
and 0.153), plausibly entangled with F11's league-wide xG scale
gap. Neither becomes a covariate: the template's §3 rejection of
a standalone on-target-rate covariate stands (v5's internal
Beta-Binomial ratio is an architectural component, tested by
the RS arm), and no template arm consumes finishing. Both
numbers are recorded for a possible future prereg — nothing is
built on them in this one.

**F7 — xGOT attacking trait is WEAK and its era is one dev
season deep.** Era-guarded (2024/2025 onward, where xGOT is
populated for ~all shots): split-half r ≈ **0.35** (≥20-match
teams, era pooled incl. partial 2026/2027; 2024/2025 alone:
0.459 on a single season). J1 measured 0.518 and adopted X6;
AU 0.543 adopted; DK 0.212 dropped. IN sits between, but the
decisive fact is structural: the era starts in the LAST dev
season, so an X6 arm would be inactive for two of three dev
seasons and effectively untestable at the dev gate (the BR X6
problem in milder form). Verdict: **DROPPED — X6 not built.**
S-IN runs Gate Zero / RS / X4.

**F8 — Referee strictness is NOT MEASURABLE in IN.** Coverage:
7/115, 14/117, 17/139, 22/163 in the dev seasons (13.5%
pooled), **0/91 in the virgin**, 28/28 only in the reserved
2026/2027. The most frequent named referee has 11 matches —
no split-half trait can even be computed. Verdict: **X8
DROPPED on coverage alone; no referee arm is built.** K-IN
runs Gate Zero only. (This is a data-availability fact about
the feed, recorded plainly.)

**F9 — Territorial pressure: box touches elite here too.**
Opp-box-touches-for split-half r = **0.783**, against r =
**0.850**. Possession-for r = 0.910 and big-chances-for
r = 0.502 — the production Gate Zero covariates (X9) are
strong in IN. Verdict: **SIGNAL-CANDIDATE** — X7 box-touch
multiplier arm vs a genuinely strong Gate Zero, as in
J1/DK/AU (where β fitted to 0 every time; the gate decides).

**F10 — Star absence: not re-tested.** The question is CLOSED
by V10 (top-5) and its J1 replication; squad churn does not
reopen it without new reliability evidence, and none was
sought. Lineup/absence features remain forbidden.

**F11 — FotMob xG runs LOW in this league.** Goals/xG pooled
≈ **1.19**; per season 1.228 / 1.185 / 1.150 / 1.202 / 1.163 /
1.086 — a systematic scale gap unlike AU (1.002) or J1
(0.98–1.08). The blend's xG observations therefore understate
goal expectation league-wide; a *uniform* scale mostly moves
the league mean inside the DC fit, but team-level differentials
in the gap (F6's finishing trait) are exactly what the fit
cannot distinguish from attack strength. Verdict: **SIGNAL
(input quality, with caveat)** — X1 adopted as the unmodified
reference pattern (Gate Zero must be the production pattern,
not a straw man); the caveat is recorded against G-IN in
advance, and no rescaling is invented inside this prereg.

**F12 — Feasibility, with the program's hardest small-n
warning.** Every target (goals, SOT, corners, event yellows,
total shots) exists for all 653 matches **including the virgin
season 2025/2026** — all five candidates are buildable:
G-IN, S-IN, C-IN, K-IN, T-IN. But the pools are the program's
smallest: dev scored n=419, virgin **n=91** — calibration SEs
~5pp, so PROVISIONAL is the realistic pass currency and a clean
PASS would be strong evidence. No candidate is declared
not-buildable: each has ≥419 dev matches behind its gate and a
complete virgin to read. Windows: dev = 2021/2022–2024/2025
(n=534), virgin = 2025/2026 (n=91, complete), confirmatory
2026/2027 reserved un-read.
