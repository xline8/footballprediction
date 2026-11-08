# Stage A — EDA: USA MLS

All headline values below come from `eda_summary.json`; 2026 is excluded except for the explicitly labelled inventory note. The modelled pooled sample is 2,544 matches (2021–25); dev is 2022–24 and virgin is 2025 (n=540).

## Findings

**F1 — Levels drift.** Goals by season are 2.782, 2.965, 2.758, 3.115, 3.017; pooled home/away goals are 1.693/1.237, a +0.456 home edge. Pooled SOT/corners/shots/yellows are 9.119/9.833/25.610/4.047.

**F2 — Core traits are reliable.** Split-half r: goals-for .516, goals-against .614, shots-for .725, SOT-for .655, corners-for .582, yellows-for .571, xG-for .659.

**F3 — Halves constants are frozen, not team features.** On complete 2024–25 period-split matches, first-half shares are goals .445, SOT .450, corners .464, shots .456, yellows .341; true variances are -.00353, .00123, .00329, .00074, .00398 respectively. These are presentation constants only.

**F4 — No mover tier exists.** MLS has no relegation/mover population. Thin expansion teams are handled by the sanctioned SHR arm.

**F5 — Set-play xG share is reliable:** r=.684.

**F6 — xG/shot is reliable:** r=.559. Finishing goals-minus-xG is below the noise bar at .238; SOT rate .376 and goals/shot .368 are not adopted as standalone features.

**F7 — xGOT era check.** Using the required era guard from 2024-01-01, the EDA population is 1,062 matches / 2,124 team-matches and r=.355. It clears the ~.3 screen, so X6 remains an arm candidate; the short era still goes to the dev gate.

**F8 — Referee strictness is reliable:** r=.634 across 32 referees with at least 20 modelled matches; named-referee coverage is 0% in 2021 and 96.1% in 2025.

**F9 — Territorial traits are reliable.** Box touches-for/against r=.711/.695; corner correlation is .513 with box touches versus .343 with possession (n=3,367 team-matches). Coverage is 100% only in 2024–25.

**F10 — Expansion is descriptive only.** First MLS-season match-level goals/xG (matches involving the club in its entry season): Charlotte 2022, n=34, 2.824/2.574; St. Louis City 2023, n=36, 3.194/2.736; San Diego FC 2025, n=39, 3.103/2.997. Expansion clubs do not enter weak on these levels — the thin-team risk is variance (zero history at entry), not a measured level gap, which is exactly what the SHR shrinkage arm addresses.

**F11 — xG calibration.** Goals/xG by 2021–25 are 1.049, 1.041, 1.042, 1.054, 1.011; pooled 1.039.

**F12 — Phase levels.** Regular goals are 2.933; playoff goals are 2.867. Both phases remain in every window.

The reserved 2026 inventory is 510 regular matches, with no playoffs; its levels are not used in any table feeding design decisions.
