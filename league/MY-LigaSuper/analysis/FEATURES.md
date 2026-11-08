# Feature decision — Malaysia Liga Super

Phase A adds no fitting code. Only adopted features and explicitly permitted architectural components may enter Phase B.

## 1. X1–X9 decisions

| Feature | Decision | Malaysia reason |
|---|---|---|
| X1 goals / xG blend | ADOPTED as goals-only | FT scores are complete; no xG anywhere. The documented blend fallback is goals-only. |
| X2 mover tier offset | DROPPED | Malaysia has only league ID 8985 in the warehouse; no sibling league. |
| X3 set-play xG | DROPPED | Stats null 793/793. |
| X4 xG per shot | DROPPED | Shotmap shots empty 793/793. |
| X5 trailing target rates | DROPPED as a feature; retained only for the preregistered naive baseline | No validated additional target arm exists. |
| X6 xGOT per shot | DROPPED | No xG or shotmap. |
| X7 opp-box touches | DROPPED | Stats absent 793/793. |
| X8 referee yellow rate | DROPPED | Referee named 0/793 and plain Yellow events 0. |
| X9 possession/big chance | DROPPED | Stats absent 793/793. |

## 2. Rejected feature families

Half-share modelling is rejected by F3: variance/noise ratio .926946 and implied true variance zero; retain only the frozen 0.4534 presentation constant. Finishing and form are rejected because there is no xG/stat feed and no reliability evidence. Lineup/absence features are rejected because lineup content is non-null in only 3/793 and no validated feature can be formed. Standings, H2H, and table snapshots are leakage risks. Attendance is not a pre-match target. Red cards are rare and there is no plain Yellow target; they are not a target feature.

## 3. Consumption map

G-MY consumes goals-only observations and the reference Dixon-Coles architecture. Gate Zero uses league-mean entrant expectations; SHRINK applies the sanctioned prior-match attenuation. There is no X2 arm. S-MY, C-MY, K-MY, and T-MY are not buildable.
