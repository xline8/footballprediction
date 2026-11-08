# Step 3 — Exploratory data analysis

All outcome analysis below uses only regular played matches from 2021/2022–2024/2025. The two virgin seasons are inventory-only elsewhere in this Phase A package.

## Levels

| season | n | goals/match | home/away goals | OU2.5 | BTTS | draw | home win |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2021/2022 | 367 | 1.981 | 1.125 / 0.856 | 0.343 | 0.420 | 0.349 | 0.398 |
| 2022/2023 | 355 | 2.180 | 1.166 / 1.014 | 0.400 | 0.470 | 0.327 | 0.392 |
| 2023/2024 | 369 | 2.301 | 1.146 / 1.154 | 0.404 | 0.469 | 0.350 | 0.336 |
| 2024/2025 | 380 | 2.263 | 1.247 / 1.016 | 0.392 | 0.437 | 0.258 | 0.445 |

The 2023/2024 row is regular-only; its three playoff matches are not in this table. Pooled dev n=1,471, goals/match=2.182, and home advantage is +0.162 goals. Away goals exceeded home goals in 2023/2024, so the home edge is weak and unstable.

## Findings

**F1 — Goals drift upward from the early dev season.** Regular goals/match move 1.981 → 2.180 → 2.301 → 2.263. This is a descriptive level fact and supports league-local, time-decayed fitting.

**F2 — Team goal traits ARE reliable at career scale.** Odd/even
chronological split-half correlations over dev-era team-match observations
(minimum 12 observations per team, 25 teams): r = 0.769 for goals-for and
r = 0.772 for goals-against. Corroboration: season-block split (2021/2022–
2022/2023 vs 2023/2024–2024/2025 team means, n=20 teams) gives 0.735 /
0.293, and team-season odd/even split (n=80 team-seasons) gives 0.613 /
0.635. The against-trait is weaker across the era boundary, consistent
with the F1 drift and roster turnover. This supports the Dixon–Coles
ratings as architectural fitted state (they encode real team differences);
no separate trailing goals covariate is added, since the ratings already
carry team strength and trailing windows attenuate the career-scale
signal. (An earlier draft of this finding reported near-zero correlations
from a misaligned split; it was re-derived by three independent splits
and corrected before the prereg commit.)

**F3 — The halves constant is presentation-only.** On 315 event-verified regular 2024/2025 matches, 798 event goals reconcile to the score and 345 occur before the explicit HT marker: frozen `goals_1h_share = 345/798 = 0.4323308271`. Per-match first-half share SD is 0.356 across the 307 matches with at least one goal; the sparse count denominator makes this compatible with sampling noise, not a team feature. Per-team halves are rejected.

**F4 — Goal-event reconciliation is exact in the 2024/2025 event era.** All 315/315 event-bearing regular matches reconcile event goal counts to the final score. In 2025/2026, the inventory check finds 352 event-bearing matches and 349/352 score reconciliations; this is reported as a data-quality count only, with no virgin goal rate.

**F5 — Reds are descriptive and rare, not a target.** Dev event-bearing matches contain 80 red-card variants over 315 matches (0.254 per event-bearing match); the 2024/2025 card taxonomy is 78 Red + 2 YellowRed and zero Yellow. Events are absent in the earlier seasons. The event taxonomy is Red plus YellowRed, with no Yellow target.

**F6 — Referee coverage is zero.** Referee text is empty in 2,032/2,032 payloads. Referee strictness cannot be estimated.

**F7 — Format and roster turnover require id-keyed state.** The league keeps 20-team/38-round structure, while 2–3 clubs turn over each season. The payload audit found no display-name changes under a stable team id in this corpus; the implementation nevertheless keys on ids as required by the programme precedent.

**F8 — No cross-league prior exists.** The warehouse index has no other Iraq league. There is no parent/sibling tier from which to estimate X2 mover offsets.
