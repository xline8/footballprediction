# Phase 3 — EDA: Australia A-League (2021/2022 – 2026/2027)

Computations on `data/au_matches.csv` (n=857; 13 teams ever;
split-half checks are career-pooled per team, ≥24 matches/team, 60
random splits averaged — with only 13 teams, |r| under ~0.3 has a
wide interval and is treated as weak at best, the same standard as
J1/DK). Virgin-window discipline: design-level aggregates only; no
fitting touched 2025/2026.

## Levels

| Season | Goals | SOT | Corners | Yellows | Shots | xG |
|---|---|---|---|---|---|---|
| 2021/2022 | 2.90 | 9.51 | 10.80 | 3.98 | 27.72 | 2.90 |
| 2022/2023 | 3.07 | 9.82 | 11.06 | 4.20 | 27.04 | 3.10 |
| 2023/2024 | 3.29 | 10.98 | 11.73 | 3.69 | 30.19 | 3.28 |
| 2024/2025 | 3.26 | 9.66 | 9.99 | 3.31 | 28.02 | 3.02 |
| 2025/2026 | 2.82 | 9.39 | 10.19 | 3.61 | 28.09 | 2.99 |
| 2026/2027 (partial) | 2.83 | 8.39 | 9.48 | 3.52 | 24.43 | 2.76 |
| **Pooled** | **3.07** | **9.84** | **10.72** | **3.74** | **28.12** | **3.05** |

Home/away goals 1.66/1.40 (home edge +0.26); HW/D/AW
41.5/25.8/32.7%; Over 2.5 = 60.0%, BTTS = 60.8%. Dispersion
(var/mean): goals 0.99, SOT 1.14, corners 1.18, yellows 0.90,
shots 1.46 (the most over-dispersed count in the program so far).

Context: AU is the highest-scoring league in the program — goals
3.07 vs top-5 2.84, DK 2.90, J1 2.55; shots 28.12 vs DK 26.02 and
J1 ~24; corners 10.72 vs DK 9.98, J1 9.47; SOT 9.84 vs DK 9.22,
J1 8.08; yellows 3.74 — between DK 3.51 and the top-5's 4.04.
Levels are league facts; the 1-league-1-model rule stands.

## Findings

**F1 — Levels drift by season, with a 2023/2024 spike.** Goals
climb 2.90 → 3.29 by 2023/2024 then fall back to 2.82 in the
virgin season; 2023/2024 spikes on every volume stat (shots
30.19, SOT 10.98, corners 11.73 — medians confirm it is a real
level shift that season, not a few outliers); corners drop to
9.99 in 2024/2025; yellows step down (4.20 → 3.31) then partly
recover. Verdict: **SIGNAL** (descriptive). Per-league,
time-decayed fitting as in production; trailing baselines adapt
faster than ratings to level steps. The virgin season ran COOLER
than dev on goals (2.82 vs dev 3.13) — calibration legs will feel
this.

**F2 — Core team traits are reliable, cards the exception.**
Career split-half r: shots-for 0.824, SOT-for 0.678,
corners-for 0.716, xG-for 0.655, goals-against 0.661,
goals-for 0.473, **yellows-for 0.351 (weak)**. Verdict:
**SIGNAL** for goals/SOT/corners/shots ratings architectures;
cards ratings rest on the weakest trait in the league — noted
against K-AU before its gate is even run.

**F3 — Half shares are noise, again.** True variance of the
per-match 1H share (observed − binomial floor at the pooled
share), complete era: goals −0.005, SOT −0.003, corners +0.001,
shots +0.000 — zero or below the floor. Yellows show a small
positive excess (+0.008) but the same frozen-constant treatment
applies — a level fact about the league constant, not a team
tendency. **Frozen AU constants (complete-splits era
2023/2024–2025/2026, ratio of sums, n=571; goals from events):
goals 0.432, SOT 0.456, corners 0.452, total shots 0.451,
yellows 0.308.** Verdict: **NOISE — constants adopted.** AU plays
slightly less of its game before half-time than DK (corners
0.452 vs 0.488) and slightly more than J1 (goals 0.432 vs 0.412).

**F4 — No relegation, no tier bridge.** The A-League has no
feeder tier in or out of the corpus, so no cross-tier offset can
exist. What remains is the thin-data problem in expansion form:
Auckland FC opened 2024/2025 with 0 in-league matches, exactly
the G-J2 failure mode (extreme lambdas for 1–2-match teams in
season openers). The sanctioned response is a pre-registered
shrinkage arm in the goals candidate — nothing else.

**F5 — Set-play xG share is a strong team identity.** Split-half
r = **0.724** (ratio of sums, stats-feed splits, all seasons) —
the strongest set-play signal in the program (J1: 0.621,
DK: 0.567). Verdict: **SIGNAL-CANDIDATE** — justifies the X3
decomposition arm in G-AU, gated against Gate Zero.

**F6 — Shot quality is real; outcomes weak.** xG/shot split-half
r = **0.576** (J1: 0.437, DK: 0.348 — strongest here);
on-target rate r = 0.321 (weak); finishing (goals − xG) r =
−0.175 → **NOISE**. Design consequence: S-AU keys on volume +
xG/shot (X4 arm); the ratio-shrink arm (RS) still tests whether
v5's ratio component earns its place; no finishing / conversion
/ standalone on-target-rate covariates.

**F7 — xGOT attacking trait PASSES its reliability check here.**
Era-guarded (2024/2025 onward, where xGOT is populated for ~100%
of shots): split-half r = **0.543** (13 teams ≥20 era matches).
Verdict: **SIGNAL-CANDIDATE — X6 analogue ADOPTED as an arm**
(J1 measured 0.518 and adopted it; DK measured 0.212 and dropped
it; AU replicates the J1 side). S-AU therefore runs the full
four-arm J1 form.

**F8 — Referee strictness is NOT a trait in AU, and coverage is
incomplete.** Referee yellow-rate split-half r = **0.06**
(10 referees with ≥20 matches) — pure noise, against J1 0.646
and DK 0.561. Coverage is also the program's worst: 76.7%
(2021/2022) to 82.8% in the virgin season, vs 100% in DK.
Verdict: **NOISE — X8 analogue DROPPED; no referee arm is
built.** K-AU runs Gate Zero only. This is a league fact about
the recorded data, recorded plainly: with r = 0.06 there is
nothing for a referee covariate to explain.

**F9 — Territorial pressure: box touches elite here too.**
Opp-box-touches-for split-half r = **0.843**, against r =
**0.882**. Possession-for r = 0.890 and big-chances-for
r = 0.502 — the production Gate Zero covariates (X9) are strong
in AU. Verdict: **SIGNAL-CANDIDATE** — X7 box-touch multiplier
arm vs a genuinely strong Gate Zero, as in J1/DK (where β fitted
to 0 both times; the gate, not optimism, decides).

**F10 — Star absence: not re-tested.** The question is CLOSED
by V10 (top-5) and its J1 replication; no new reliability
evidence exists in this corpus and none was sought.
Lineup/absence features remain forbidden.

**F11 — FotMob xG is calibrated for AU.** Goals/xG pooled
1.002; per season 0.944–1.080. Verdict: **SIGNAL** (input
quality) — the production blend has a sound input here from
the first season (no goals-only era, unlike J1 2021).

**F12 — Feasibility, with a small-n warning.** Every target
(goals, SOT, corners, yellows, total shots) exists for all 857
matches **including the virgin season 2025/2026** — all five
candidates are buildable: G-AU, S-AU, C-AU, K-AU, T-AU. But the
pools are the program's smallest so far: dev walk-forward
scores n=508 matches (2022/2023–2024/2025) and the virgin is
n=163, so calibration SEs run ~3.5–4pp and PROVISIONAL outcomes
are more likely than in DK/AT. Windows: dev = 2021/2022–
2024/2025 (n=671), virgin = 2025/2026 (n=163, complete),
confirmatory 2026/2027 reserved un-read.
