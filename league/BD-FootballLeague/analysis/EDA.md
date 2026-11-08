# Phase 3 — EDA

Tool: `analysis/eda.py`; raw outputs are `inventory_summary.json` and
`eda_summary.json`. Dev is 2022/2023–2025/2026 (n=365), evaluation is
2023/2024–2025/2026 (n=270), virgin primary is the in-progress 2026/2027
(n=29 through 2026-10-24), and 2026/2027 levels are descriptive only beyond
the gate.

## Findings

**F1 — levels and drift.** Goals/match by season are 2.958, 2.922, 3.122,
2.611, and 3.690 (in progress). Dev pooled is 2.904. Home-win rates are
0.379, 0.278, 0.444, 0.400, and 0.379; OU2.5 rates are 0.495, 0.544, 0.533,
0.456, and 0.690. The 2025/2026 dip (2.611) and the 2026/2027 spike (3.690,
n=29) are the extremes; there is no monotone drift across the four complete
seasons.

**F2 — trait reliability.** Chronological split-half r for GF is 0.529, 0.787,
0.704, 0.637; GA is 0.819, 0.925, 0.830, 0.698. Teams need at least five
matches in each half. Both traits are reliable in every season, which is the
entire justification for a scores-only ratings fit.

**F3 — halves.** Dev 1H share is 447/1060 = 0.4217 across 365 matches;
per-season shares are 0.3986, 0.4297, 0.4270, and 0.4340. Per-match variance
is 0.1050 versus binomial 0.1067 (excess −0.0017). The frozen constant is
presentation-only. The team-level split-half calculation (interleaved
odd/even matches per team across dev) returns r=0.207 (n=16 teams) — weak,
positive, and on a small team count; with excess variance below zero it does
not support any per-team 1H-share trait. No per-team or per-match halves
model is allowed.

**F4 — entrants.** The five real post-seed entrants are Brothers Union
2023/2024 (GF −0.29 / GA +2.21), Dhaka Wanderers 2024/2025 (−0.78 / +1.49),
Fakirerpool 2024/2025 (−0.28 / +1.44), Arambagh 2025/2026 (−0.64 / +0.25),
and PWD SC 2025/2026 (−0.47 / +0.25). The five-entrant mean is GF −0.49 and
GA +0.93 — new clubs score less and concede far more, with the defensive gap
dominant. There is no sibling league and no independent prior, so this is
descriptive only; no entrant arm is registered. The 2026/2027 entrants (City
Club, Chattogram City) are descriptive only, as is the returning Mohammedan.

**F5 — coverage.** Stats, shotmap shots, named referees (except 33 matches),
playerStats, and period splits are 0/394 in dev; events and HT markers are
394/394. Lineups with 11 starters both sides are 394/394 but unused.

**F6 — identity.** Eighteen ids are present; no id has more than one spelling.
Chittagong Abahani and Chattogram City are different ids and different clubs.

**F7 — format.** There is no split group or playoff. 2022/2023 is missing
rounds 1–3 (15 matches) from the warehouse. 2023/2024–2025/2026 are complete
10-team double round-robins. 2026/2027 expands to 13 teams; round 4 has one
fixture missing from the index.

**F8 — virgin.** 2026/2027 is in progress with 29 matches through 2026-10-24
and is the primary virgin window (TRANSITIONAL). Its levels (3.690 goals/match,
OU2.5 rate 0.690) are far above dev norms on a tiny n; the gate arithmetic
still applies mechanically, but the calibration SEs will be wide (~9pp) and
the season-end confirmatory read is required before any production use. There
is no complete virgin season available for this league.

**F9 — target feasibility.** Goals are consistently available. S/C/T have no
stats or shots. Plain Yellow is absent in every season, while Red/YellowRed
total 59; K is not buildable.

**F10 — event completeness.** Zero matches lack events. Zero score/event
mismatches; the official score is retained everywhere. HT cross-check agrees
363/363.

**F11 — line selection.** Evaluation pooled OU1.5/2.5/3.5 rates are 0.781,
0.511, and 0.333; OU2.5 is the primary line. Evaluation pooled home-win is
0.374.

**F12 — home advantage.** Dev pooled home-win rate is 0.375 (away-win 0.348 —
an unusually small home edge). The goals architecture fits home advantage; no
separate home-edge feature is added.

**F13 — SHRINK bite.** Prior bands are: 2022/2023 11 teams at zero;
2023/2024 9 at 6–23 and 1 at zero; 2024/2025 7 at 24+, 2 at zero, 1 at 6–23;
2025/2026 7 at 24+, 2 at zero, 1 at 6–23; 2026/2027 8 at 24+, 3 at 6–23, 2 at
zero. No target-season start has a team in the 1–5 band.

**F14 — thin dev windows.** The dev evaluation is only n=270 across three
seasons (90 each), with a 95-match incomplete seed. A single season's LL
moves by ~±0.05 on sampling noise alone; the pooled gate is the decision
unit and per-season numbers are reported for diagnosis only.
