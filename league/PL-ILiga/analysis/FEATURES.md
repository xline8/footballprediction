# Phase 3.5 — Feature Engineering: Poland I Liga

The causality contract is inherited from the J1 X1–X9 template: only strictly pre-match information, trailing/expanding windows, ratio-of-sums, and signed-age fit state are admissible.

## X1–X9

- X1 — ADOPTED. Goals-only observation pair for the production DC pattern. xG is absent in all seasons, so there is never a blend input.
- X2 — DROPPED. Same-league newcomer gaps are +0.059 GF and +0.05 GA pooled. Direction gaps are Ekstraklasa +0.145 GF / -0.032 GA and II Liga -0.028 GF / +0.131 GA, with changing per-transition signs; no stable directional prior is justified.
- X3 — DROPPED. Set-play xG is absent in all seasons.
- X4 — DROPPED. Shotmap xG and shots are absent in all seasons.
- X5 — DROPPED. SOT/corners/yellow target-rate feeds are absent; card events have no Yellow source.
- X6 — DROPPED. xGOT/shotmap xGOT is absent.
- X7 — DROPPED. Opponent-box touches are absent with the stats feed.
- X8 — DROPPED. Referee identity/text is absent; referee coverage is 0.0%.
- X9 — DROPPED. Possession and big chances are absent with the stats feed.

## Halves constants

The goals 1H share is frozen at 0.457 because estimated true variance is -0.0033 and true SD is 0.0. SOT, corners, shots, and cards have no halves inputs and remain FT-only; no constant is created for them.

## Rejected list

R1 team first-half shares are presentation-only, supported by the goals variance result above. R2 finishing, R3 conversion, R4 on-target rate, R5 defensive xGOT, R6 lineups/absence, R7 shooter concentration, R8 formation/coach, R9 standings/h2h/teamForm, R10 attendance, R11 game-state, R12 red-card target/covariate, and R13 momentum are rejected as absent, leakage-prone, outcome-contaminated, or unsupported. R12 is additionally a rare-event rejection; the only card source is Red/YellowRed and there is no Yellow source.

