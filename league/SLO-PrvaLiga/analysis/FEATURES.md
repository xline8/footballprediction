# Feature decision — SLO-PrvaLiga

Only adopted features and explicitly permitted architectural components may enter a later model phase. Phase A adds no engine or fitting code.

## 1. Accepted

X1 goals-only observations — ADOPTED. Official FT scores are complete in 956/956 payloads; xG is unavailable because stats are null in 956/956. X5 trailing target-rate means — ADOPTED only as the naive baseline component, not as an additional G-SLO covariate. The ratings, home intercept, DC correction, decay, and SHRINK are architectural components.

## 2. Architectural components

Ratings, home advantage, Dixon-Coles rho, MAXG=10, time decay, league climatology, naive trailing-10, and Gate Zero/SHRINK are model architecture or evaluation baselines, not free covariates. The frozen halves constant is presentation-only.

## 3. X1–X9 decisions

| Feature | Decision | SLO reason |
|---|---|---|
| X1 goals / xG blend | ADOPTED as goals-only | Scores complete; stats null 956/956 |
| X2 mover tier offset | DROPPED | Complete index has only league 173 for Slovenia; no sibling prior |
| X3 set-play xG | DROPPED | Stats null 956/956 |
| X4 xG per shot | DROPPED | Shotmap empty 956/956 |
| X5 trailing target rates | ADOPTED for naive baseline only | No SOT/corners/yellow target arm is buildable |
| X6 xGOT per shot | DROPPED | No shotmap/xG |
| X7 opp-box touches | DROPPED | Stats absent 956/956 |
| X8 referee yellow rate | DROPPED | Referee named 0/956; plain yellows 0 |
| X9 possession/big chance | DROPPED | Stats absent 956/956 |

## 3b. R1–R13 analogues

| Analogue | Decision and measured reason |
|---|---|
| R1 team first-half shares | DROPPED: variance ratio .936361, implied true SD .0000; retain only .4498 presentation constant |
| R2 finishing | DROPPED: no xG, stats null 956/956 |
| R3 conversion | DROPPED: shotmap empty 956/956 |
| R4 on-target rate | DROPPED: shotmap empty 956/956 |
| R5 defensive xGOT | DROPPED: no xG/shotmap |
| R6 lineups/absences | DROPPED: lineup non-null 32/956, with no validated feature |
| R7 shooter concentration | DROPPED: no eligible shot data |
| R8 formation/coach | DROPPED: no validated feature; lineup is sparse |
| R9 standings/H2H snapshots | DROPPED as leakage |
| R10 attendance | DROPPED as post-match |
| R11 first-goal/game-state | DROPPED as in-match |
| R12 reds | DROPPED as target/covariate: 125 Red and 51 YellowRed, zero plain Yellow |
| R13 momentum | DROPPED as in-match |

## 4. Consumption map

G-SLO consumes X1 goals-only observations and the reference DC architecture. Gate Zero starts entrants at league mean. SHRINK applies the sanctioned prior-match attenuation. NO ENTRANT is declared as a no-mover arm because X2 is unavailable. S/C/K/T are not buildable.
