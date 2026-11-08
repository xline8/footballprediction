# Phase 5 — Features: PT-LigaPortugal (J1 template X1–X9)

Same causality contract as J1's FEATURES.md: features for a match use
only matches strictly before it (season-blocked fits in the engines
below use only seasons strictly before the target season); ratio
features are ratios of sums; a window that cannot be filled makes
the arm inactive for that match — never imputed from the future.

| # | J1 template feature | PT verdict | Reason (PT number) |
|---|---|---|---|
| X1 | Blend observation pair (goals + xG) | **ADOPTED** | xG present in 1,628/1,628 matches, all seasons; goals/xG totals track (2.55–2.76 xG vs 2.49–2.87 goals per season). |
| X2 | Cross-tier mover offset | **DROPPED** | The tier gap cannot be measured from this league's own corpus (no Liga 2 pull in scope), and hard-coding J1's magnitudes into a European league would be fabrication. The underlying problem — thin-history teams in season openers (G-J2 post-mortem) — is addressed instead by the goals candidate's pre-registered shrinkage arm (template-sanctioned). |
| X3 | Set-play xG share/rate | **DROPPED** | Reliability fails in this league: split-half r = 0.27 (J1: 0.62). Below the bar J1 itself set; not consumed. |
| X4 | xG per shot (trailing) | **ADOPTED** (SOT variant arm) | Split-half r = 0.63. Shotmap complete in all seasons. |
| X5 | Trailing target-rate means (naive/ensemble) | **ADOPTED** | Every target trait is reliable: SOT-for 0.89, corners-for 0.71, yellows-for 0.61, shots-for 0.80. |
| X6 | Attacking xGOT per shot (era-guarded) | **ADOPTED** (SOT variant arm, era 2024/2025+) | r = 0.59 (n=20 teams) in the era where xGOT is populated for ~all shots; era guard is structural (pre-2024/25 xGOT covers on-target shots only). |
| X7 | Opp-box touches for/against | **ADOPTED** (corners variant arm) | r = 0.88 for / 0.74 against — the strongest territorial trait here. Coverage caveat: partial (209–252/season) until 2024/2025, complete after; the min-matches rule governs activation. |
| X8 | Referee yellow rate | **ADOPTED, weak** (cards variant arm) | r = 0.28 (n=25) — much weaker than J1's 0.65, adopted only as a shrunk variant arm so the gate can kill it; coverage 53% in 2021/2022, ~100% from 2023/2024. Pre-match publication cannot be proven from post-match snapshots; fixtures without a named referee fall back to Gate Zero (no imputation). |
| X9 | Production corners covariates (possession, big chances) | **ADOPTED** (corners Gate Zero) | Possession r = 0.88, big-chance-for r = 0.89; carried unchanged so Gate Zero is the true production pattern. |

Rejected outright (J1 §3 analogues, re-checked where data allows):
team 1H shares (true variance ≈ 0 for goals/SOT/shots, team r ≤ 0.25
for all five — frozen constants only, below); trailing finishing
(r = 0.26); yellows-against as a covariate trait (0.17, noise; it
remains part of the ratings state, not a feature); standings/h2h/
teamForm snapshots (post-match leakage); lineup/absence features
(closed program-wide; no new evidence offered here).

## Frozen half-share constants (presentation only)

From the complete period-split era (2023/2024–2025/2026),
ratio-of-sums over all split matches: **goals 0.443, SOT 0.449,
corners 0.471, yellows 0.331, total shots 0.456**. Second half is
the complement. These are the only halves mechanism.

## Consumption map

| Candidate | Base | Variant arms |
|---|---|---|
| G-PT goals | X1 | shrinkage arm (thin-history teams) |
| S-PT SOT | X5 + v5 architecture (shots ratings, BB ratio, naive ensemble) | X4, X6 (era) |
| C-PT corners | X5 + X9 (Gate Zero multiplier) | X7 |
| K-PT cards | X5 | X8 (shrunk referee multiplier) |
| T-PT total shots | X5 + v1 pattern (ratings + NB + naive ensemble) | E9-style trailing-r |
