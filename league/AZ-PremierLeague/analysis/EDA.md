# Phase 3 — EDA

Tool: `analysis/eda.py`; raw outputs are `inventory_summary.json` and
`eda_summary.json`. Dev is 2021/2022–2024/2025 (n=652), evaluation is
2022/2023–2024/2025 (n=540), virgin primary is 2025/2026 (n=198), and
2026/2027 (n=64) is descriptive only.

## Findings

**F1 — levels and drift.** Goals/match by season are 2.598, 2.639, 2.617,
2.400, 2.591, and 2.562. Dev pooled is 2.560. Home-win rates are 0.411,
0.400, 0.439, 0.406, 0.374, and 0.438; OU2.5 rates are 0.491, 0.517,
0.483, 0.406, 0.485, and 0.484. There is no monotone drift.

**F2 — trait reliability.** Chronological split-half r for GF is 0.75,
0.89, 0.74, 0.87; GA is 0.69, 0.70, 0.66, 0.70. Teams need at least five
matches in each half.

**F3 — halves.** Dev 1H share is 725/1669 = 0.4344 across 605 matches;
per-season shares are 0.4433, 0.4063, 0.4289, and 0.4653. Per-match
variance is 0.1178 versus binomial 0.1219 (excess -0.0040). The frozen
constant is presentation-only. The script's team-level split-half calculation
(interleaved odd/even matches per team across dev) returns r=-0.38 (n=11
teams); the chronological first/second-half variant returns r=0.04 (n=35
season-team pairs). Both agree there is no reliable per-team 1H-share trait
(the interleaved value is negative, the chronological value is ~0).

**F4 — entrants.** The script measures post-seed entrants as FC Kapaz
(-0.38/+0.40), Turan Tovuz (-0.32/+0.04), Araz PFK (-0.45/+0.08), Karvan FK
(-0.60/+0.70), and Imisli FK (-0.60/+0.01). The five-real-entrant mean is
GF -0.45 and GA +0.25. Shafa in 2026/2027 is descriptive only.

**F5 — coverage.** Stats, shotmap shots, named referees, lineups, and
playerStats are 0/914; events and HT markers are 844/914.

**F6 — identity.** Fourteen ids are present; only 2103, 7981, and 213987
have more than one spelling. Id 2103 is the Keshla/Shamakhi FK rename.

**F7 — format.** There is no split group or playoff. The 2025/2026 expansion
is the only schedule change; 2026/2027 is incomplete and has missing round-2
fixtures in the warehouse index.

**F8 — virgin.** 2025/2026 is complete with 198 matches and is the primary
virgin window. 2026/2027 has 64 matches through 2026-11-08 and is confirmatory.

**F9 — target feasibility.** Goals are consistently available. S/C/T have no
stats or shots. Plain Yellow is absent in every season, while Red/YellowRed
total 154; K is not buildable.

**F10 — event completeness.** Seventy matches have no events. The one score
event mismatch is 4946647; the official 0–3 score is retained.

**F11 — line selection.** Evaluation pooled OU1.5/2.5/3.5 rates are 0.704,
0.469, and 0.274; OU2.5 is the primary line. Evaluation pooled home-win is
0.415.

**F12 — home advantage.** Dev pooled home-win rate is 0.414. The goals
architecture fits home advantage; no separate home-edge feature is added.

**F13 — SHRINK bite.** Prior bands are: 2022/2023 2 teams at zero and 8 at
24+; 2023/2024 1 at zero and 9 at 24+; 2024/2025 10 at 24+; 2025/2026 2 at
zero and 10 at 24+; 2026/2027 1 at zero and 11 at 24+. No target start has a
team in the 1–5 band.

**F14 — 2026/2027 restriction.** Its levels and coverage are descriptive only;
it is not used for fitting, reliability, or a gate.
