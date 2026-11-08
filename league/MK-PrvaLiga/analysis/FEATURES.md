# Feature decision — MK-PrvaLiga

The consumption rule is strict: only adopted features and explicitly permitted architectural components may enter a later model phase. Phase A adds no engine or fitting code.

## 1. Accepted

X1 goals-only observations — ADOPTED. Official FT goals are complete in all 1,022 payloads; xG is absent in 1,022/1,022. X5 trailing target-rate means — ADOPTED only as the naive baseline component, not as an additional G-MK covariate. The goals ratings, home intercept, DC correction, decay, and SHRINK are architectural components.

## 2. Architectural components

Ratings, home advantage, Dixon-Coles rho, MAXG=10, time decay, league climatology, naive trailing-10, and Gate Zero/SHRINK are model architecture or evaluation baselines, not free covariates. The frozen halves constant is presentation-only.

## 3. X1–X9 decisions

| Feature | Decision | MK reason |
|---|---|---|
| X1 goals / xG blend | ADOPTED as goals-only | Goals complete; xG absent in 1,022/1,022 |
| X2 mover tier offset | DROPPED | Index has only league 249 in North Macedonia; no sibling tier corpus |
| X3 set-play xG | DROPPED | No xG/stats |
| X4 xG per shot | DROPPED | Shotmap empty 1,022/1,022 |
| X5 trailing target rates | ADOPTED for naive baseline only | No SOT/corners/yellow targets for a market arm |
| X6 xGOT per shot | DROPPED | No shotmap/xG |
| X7 opp-box touches | DROPPED | Stats absent |
| X8 referee yellow rate | DROPPED | Referee named 0/1,022; plain yellows 0 |
| X9 possession/big chance | DROPPED | Stats absent |

## 3b. R1–R13 analogues

R1 team first-half shares: DROPPED, variance ratio 0.9572 and implied true SD 0.0000; retain only the 0.4323 presentation constant. R2 finishing: DROPPED, no xG. R3 conversion: DROPPED, no shots. R4 on-target rate: DROPPED, no shots/SOT. R5 defensive xGOT: DROPPED, no xGOT. R6 lineups/absences: DROPPED, lineup non-null 4/1,022 and three are unavailable stubs. R7 shooter concentration: DROPPED, no eligible shot data. R8 formation/coach: DROPPED, no usable lineups. R9 standings/H2H snapshots: DROPPED as leakage. R10 attendance: DROPPED as post-match. R11 first-goal/game-state: DROPPED as in-match. R12 reds: DROPPED as a target/covariate; only 131 Red and 87 YellowRed events, no yellows. R13 momentum: DROPPED as in-match.

## 4. Consumption map

G-MK consumes X1 goals-only observations and the reference DC architecture. Gate Zero starts entrants at league mean. SHRINK applies the sanctioned prior-match attenuation. NO ENTRANT is a declared arm with no additional mover feature and is not separately fitted because X2 is unavailable. S/C/K/T are not buildable.
