# Phase 3 — EDA: Sweden Allsvenskan (2021 – 2026)

Computations on `data/se_matches.csv` (n=1,424; 21 teams ever;
split-half checks are career-pooled per team, ≥24 matches/team, 60
random splits averaged — with 16–21 teams, |r| under ~0.3 has a wide
interval and is treated as weak at best, the same standard as J1/DK).
Virgin-window discipline: design-level aggregates only; no fitting
touched 2025.

## Levels

| Season | Goals | SOT | Corners | Yellows | Shots | xG |
|---|---|---|---|---|---|---|
| 2021 | 2.66 | 9.01 | 10.53 | 3.63 | 27.13 | 2.99 |
| 2022 | 2.76 | 9.07 | 10.79 | 3.73 | 27.08 | 2.73 |
| 2023 | 2.77 | 8.90 | 10.46 | 3.29 | 26.40 | 2.68 |
| 2024 | 2.83 | 8.90 | 10.91 | 3.25 | 27.18 | 2.64 |
| 2025 | 2.85 | 8.92 | 10.88 | 3.77 | 27.30 | 2.88 |
| 2026 (partial) | 2.83 | 9.32 | 10.37 | 3.27 | 27.82 | 2.95 |
| **Pooled** | **2.78** | **9.01** | **10.66** | **3.50** | **27.13** | **2.82** |

Home/away goals 1.53/1.24 (home edge +0.29); HW/D/AW 43.5/23.0/33.5%
(pooled, approx. from per-season means); Over 2.5 ≈ 52.8%, BTTS
≈ 51.9%. Dispersion (var/mean): goals ≈ 1.00, SOT ≈ 1.17,
corners ≈ 1.19, yellows ≈ 0.98, shots ≈ 1.41 (shots are the most
over-dispersed target in this league — the NB family earns its keep
for T-SE).

Context: SE scores close to DK (2.78 vs 2.90) and above J1 (2.55);
corners 10.66 are the highest of the conveyor leagues so far (J1
9.47, DK 9.98); SOT 9.01 vs J1 8.08 / DK 9.22; yellows 3.50, level
with DK's 3.51 and between J1's 2.34 and the top-5's 4.04; total
shots 27.13 are high with heavy dispersion. Levels are league
facts; the 1-league-1-model rule stands.

## Findings

**F1 — Levels are broadly stable, goals drift up gently.** Goals
2.66 → 2.85 across 2021–2025 with no single step; yellows oscillate
(3.25–3.77) with no trend. Verdict: **SIGNAL** (descriptive).
Per-league, time-decayed fitting as in production.

**F2 — Core team traits are strongly reliable.** Career split-half
r: possession-for 0.924, shots-for 0.884 / against 0.851, xG-for
0.838 / against 0.842, SOT-for 0.836 / against 0.802, goals-for
0.765 / against 0.759, corners-for 0.757 / against 0.789,
yellows-for 0.707 (yellows-against only 0.263 — conceded cards are
mostly the opponent's trait, as expected). Verdict: **SIGNAL** — a
ratings architecture has real signal in every market.

**F3 — Half shares are noise, again.** True variance of the
per-match 1H share (observed − binomial floor), complete-splits era
2023–2025: goals −0.002, SOT −0.001, corners +0.003, shots +0.000 —
zero or below the floor (yellows +0.012 on 2023–2025 is driven by
the artefact-suspect 2023 FH splits; on the clean 2024–2025 era it
is +0.005, still a level fact about the league constant, not a team
tendency). **Frozen SE constants (ratio of sums): goals 0.440
(2023–2025 events, n=678), SOT 0.455, corners 0.473, total shots
0.457 (2023–2025 splits, n=720), yellows 0.370 (2024–2025 only,
n=470).** Verdict: **NOISE — constants adopted.** SE's corners 1H
share (0.473) sits between J1's 0.447 and DK's 0.488; its goals
share (0.440) is above J1's 0.412 and below DK's 0.463.

**F4 — No in-corpus tier bridge.** Promoted sides arrive from
Superettan, which this corpus does not contain, so no cross-tier
offset is estimable (contrast J1 F4; same position as DK). What
remains is the thin-data problem itself: 2–3 new sides per season
open with 0–2 in-league matches, exactly the G-J2 failure mode
(extreme lambdas for 1–2-match teams in season openers). The
sanctioned response is a pre-registered shrinkage arm in the goals
candidate — nothing else.

**F5 — Set-play xG share is a stable team identity.** Split-half
r = **0.617** (ratio of sums, stats-feed splits, all seasons).
Verdict: **SIGNAL-CANDIDATE** — justifies the X3 decomposition arm
in G-SE, gated against Gate Zero (J1 F5: 0.621; DK F5: 0.567 — SE
replicates J1 almost exactly).

**F6 — Shot quality is weak here; outcomes are noise.** xG/shot
split-half r = **0.268** (weak — J1: 0.437, DK: 0.348, NL: 0.759);
on-target rate r = 0.210 (weak); finishing (goals − xG) r = 0.272 →
**NOISE** (weak, wide interval at 21 teams). Design consequence:
S-SE still runs the X4 arm (the trait is positive and the gate, not
optimism, decides — the DK precedent at r = 0.348), but it is
recorded here as the weakest X4 evidence in the program so far; the
ratio-shrink arm (RS) tests whether v5's ratio component earns its
place; no finishing / conversion / standalone on-target-rate
covariates.

**F7 — xGOT attacking trait FAILS its reliability check here.**
Era-guarded (2025 onward, where xGOT is populated for ~100% of
shots): split-half r = **0.099**. Verdict: **NOISE — X6 analogue
DROPPED** (J1 measured 0.518; DK also failed at 0.212; SE does not
replicate it). The unguarded all-era figure (0.843) is an artefact
of the population-rule break and is not evidence. No xGOT arm is
built.

**F8 — Referee strictness is a real trait where referees are
named.** Referee yellow-rate split-half r = **0.616** (14 referees
with ≥20 matches). Coverage is the caveat: 0% in 2021, 71–88% from
2022 (84.6% in the virgin season). Verdict: **SIGNAL-CANDIDATE** —
justifies the X8 referee arm in K-SE (J1 F8: 0.646), with the
program's standard conditions: fixtures whose referee identity is
unknown (or unpublished pre-match in a live pipeline) fall back to
the base arm; no imputation.

**F9 — Territorial pressure: box touches are elite here too.**
Opp-box-touches-for split-half r = **0.872**, against r = **0.809**
(measured on present matches; coverage is 39–51% in 2021–2023 and
100% from 2024, so early trailing windows will often be inactive
under the min-8 rule). Possession-for r = 0.924 and big-chances-for
r = 0.786 — the production Gate Zero covariates (X9) are themselves
strong in SE. Verdict: **SIGNAL-CANDIDATE** — X7 box-touch
multiplier arm vs a genuinely strong Gate Zero, as in J1/DK.

**F10 — Star absence: not re-tested.** The question is CLOSED by
V10 (top-5) and its J1 replication; no new reliability evidence
exists in this corpus and none was sought. Lineup/absence features
remain forbidden.

**F11 — FotMob xG is calibrated for SE, with one soft season.**
Goals/xG per season: 0.889 (2021), 1.010 (2022), 1.035 (2023),
1.074 (2024), 0.987 (2025), 0.960 (2026 partial); pooled ≈ 0.99.
Verdict: **SIGNAL** (input quality) — the production blend has a
sound input here; 2021's 0.889 is noted (goals ran below xG) but
the blend needs no correction and none is pre-registered.

**F12 — Feasibility.** Every target (goals, SOT, corners, yellows,
total shots) exists for all 1,200 dev+virgin matches **including
the virgin season 2025** — all five candidates are buildable:
G-SE, S-SE, C-SE, K-SE, T-SE. Windows: dev = 2021–2024 (n=960),
virgin = 2025 (n=240, complete), confirmatory 2026 reserved
un-read.
