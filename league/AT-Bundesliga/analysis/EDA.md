# Phase 3 — EDA: Austria Bundesliga (2021/2022 – 2026/2027)

Computations: `eda.py` (digest in `eda_summary.json`). Sample: 1,047
matches, 15 teams. Standard, as in J1: **a trait is a signal candidate
only if it reproduces on disjoint halves of the same teams' matches
(split-half, career-pooled, ≥24 team-matches, 30 seeded splits) or
survives a variance decomposition against its sampling-noise floor.**
With 15 teams, an |r| under ~0.3 has a very wide interval and is
treated as weak evidence at best — a stricter practical bar than J1's
23–36 teams.

## Levels

| Quantity (per match) | AT-Bundesliga | J1 | Top-5 spine |
|---|---|---|---|
| Goals | 2.81 (SD 1.63) | 2.55 | 2.84 |
| Home / away goals | 1.52 / 1.29 | 1.38 / 1.18 | — |
| Home win / draw / away win % | 39.5 / 27.5 / 33.0 | 41.3 / 26.8 / 31.9 | — |
| BTTS % / Over 2.5 % | 56.6 / 53.3 | 50.4 / 47.0 | — |
| Total shots | 24.9 | 24.8 | ~25.6 |
| SOT | 8.52 | 8.08 | — |
| Corners | 9.76 | 9.47 | — |
| Yellow cards | 4.07 | 2.34 | 4.04 |
| Red cards | 0.235 | 0.11 | — |
| Team xG (stats feed) | 2.89 | 2.52 | — |

Austria is a **European-level league, not a J.League-level one**: goals
(2.81) sit on the top-5 mean (2.84), and discipline is European too —
4.07 yellows/match vs J1's 2.34. The virgin season (2025/2026) ran
cooler than dev on every counting stat (SOT 7.93 vs dev 8.58; corners
9.33 vs 9.81) — the gates will feel that.

Dispersion (variance/mean of match total): goals 0.95, SOT 1.02,
corners 1.10, shots 1.24, yellows 0.92. Near-Poisson everywhere except
total shots (the familiar shots overdispersion).

## Findings

**F1 — League levels drift by season.** Goals by season: 2.89, 2.96,
2.58, 2.75, 2.70 (complete seasons); SOT 8.79 → 7.93 across the same
span; yellows 3.88–4.49 with no trend. Home edge +0.23 goals pooled.
Verdict: **SIGNAL** (descriptive fact) — per-league levels with
time-decayed fitting, as in production.

**F2 — Core team traits are strongly reliable.** Career split-half r:
shots-for 0.896, xG-for 0.894, SOT-for 0.867, corners-for 0.828,
goals-for 0.801, goals-against 0.692, yellows-for 0.497. Verdict:
**SIGNAL-CANDIDATE (strong)** — a ratings architecture has real signal
in every market here, cards included (weaker, as everywhere).

**F3 — Half shares are noise here too, for every counting stat.**
True variance of the per-match 1H share (observed minus binomial
floor), complete-split era 2023/2024–2025/2026: goals −0.0030, SOT
−0.0061, shots −0.0014, corners +0.0004, yellows +0.0003 — zero or
below the floor in all five. Team-level 1H goal-share split-half
r = −0.38. League constants (ratio of sums, same era): goals 0.448,
SOT 0.447, corners 0.476, shots 0.454, yellows 0.316. Verdict:
**NOISE.** The halves book stays closed on a third corpus; halves
products use the frozen constants above, exactly as production does.

**F4 — No cross-tier bridge is measurable in this build.** Promoted
clubs arrive from the 2. Liga, which has no warehouse build in this
league's scope, so no mover offset can be estimated honestly.
Consequence (design-level): promoted/thin-data teams are handled by
the goals candidate's pre-registered **shrinkage arm** (the template's
sanctioned response to the G-J2 lesson), not by an X2 analogue.
Verdict: **DATA ABSENT** — recorded, not worked around.

**F5 — Set-play xG share is a stable team identity.** Split-half
r = **0.477** (15 teams). Verdict: **SIGNAL-CANDIDATE** — justifies the
goals decomposition-tilt arm, gated, as in J1.

**F6 — Shot quality is mildly real; shot outcomes are noise.**
Split-half r: xG per shot **0.480**, goals per shot 0.300 (weak,
outcome-contaminated), finishing (goals − xG) **0.100 → NOISE**,
on-target rate **−0.114 → NOISE**. Same verdicts as J1 and the top-5
autopsy: an SOT model keys on volume and xG/shot, never on trailing
conversion/finishing/SOT-rate form.

**F7 — xGOT attacking trait FAILS its reliability check here.**
Era-guarded (2024/2025+, where the field is populated for ~all shots):
split-half r = **0.273**, 13 teams. Below the 0.3 noise-zone line and
far below J1's 0.518, on a smaller team count. Verdict: **NOISE /
insufficient evidence — DROPPED** at the feature step (see FEATURES).
The era guard itself was still necessary to measure it honestly.

**F8 — Referee strictness is a real trait.** Cards per match by
referee: split-half r = **0.547** (17 referees with ≥20 matches, 852
matches with a named referee). Coverage: 81.4% overall, 91.8% in the
virgin season. Verdict: **SIGNAL-CANDIDATE** for the cards referee
arm, subject to the walk-forward gate and the pre-match availability
fallback (fixtures without a named referee fall back to the base arm;
warehouse records are post-match snapshots, so pre-match publication
cannot be proven from them — the fallback is the operating rule).

**F9 — Territorial pressure: box touches are the corners proxy, and
the strongest trait in this EDA.** Team opp-box-touches split-half
r = **0.945** (for) / 0.813 (against) — even stronger than J1's 0.857.
Per team-match, corners correlate 0.546 with own box touches vs 0.407
with possession (n=1,714). Production's own big-chance covariate is
also reliable (r = 0.873), so the gated comparison is box touches vs
a genuinely strong reference arm. Coverage caveat: box touches are
complete only from 2024/2025 (63.6% / ~58% / 80.5% before) — the arm
inherits a minimum-sample rule and falls back to Gate Zero where its
trailing window is thin. Verdict: **SIGNAL-CANDIDATE**.

**F10 — Star absence: not re-run; the question stays closed.** The
V10 protocol produced a null on the top-5 and a replicated null on J1
(F10 there); the agreed reopening standard (new reliability evidence)
is not met by anything in this EDA. Lineup/absence features remain
forbidden; no arm uses lineups.

**F11 — FotMob xG is calibrated for Austria.** Goals per unit xG by
season: 0.989, 0.998, 0.924, 0.966, 0.979 (complete seasons) — pooled
0.975. Verdict: **SIGNAL** (input quality fact) — the production blend
idea has a sound input here, in every season (no goals-only era).

**F12 — Feasibility boundary (fact).** Every market is buildable:
goals/SOT/corners/cards/total-shots targets exist for 100% of matches
in both the dev seasons and the virgin season. The constraints are
feature-side only: period splits before 2023/2024 (halves constants
therefore measured on the complete era, F3), box touches before
2024/2025 (F9 caveat), xGOT era (F7), referee gaps in 2021/2022 (F8).
