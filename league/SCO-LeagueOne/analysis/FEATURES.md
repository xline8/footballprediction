# Phase A — Feature Decisions: SCO League One

Consumption is strictly pre-match trailing/expanding state. A missing feature is inactive, never imputed.

| # | Feature | Verdict | Evidence / decision |
|---|---|---|---|
| X1 | Goals + xG blend | **DROPPED** | No xG: stats Periods content present in 0/969 payloads. |
| X2 | Mover tier offset | **ADOPTED (arm)** | Down entrants: pooled ΔGF +0.176190, ΔGA −0.288095; up_other: −0.136111, +0.200694. The gap is real for the arm criterion: directional gaps recur in all four down seasons and up GA seasons, with pooled magnitudes well above zero. |
| X3 | Set-play xG | **DROPPED** | No xG. |
| X4 | Shotmap-derived features | **DROPPED** | 0 shots in 969 matches. |
| X5 | Trailing target-rate means | **ADOPTED** | Goals r=0.410642/0.578946 for/against; event Yellow r=0.387955/0.534905. |
| X6 | xGOT | **DROPPED** | No xGOT or stats content. |
| X7 | Opponent-box touches | **DROPPED** | No stats content. |
| X8 | Referee yellow rate | **DROPPED** | 0 usable referees out of 969. |
| X9 | Possession / big chance | **DROPPED** | No stats content. |

Frozen halves constants: goals 0.429460 (true variance −0.00413859, NOISE) and event Yellow 0.314062 (true variance +0.00002057). SOT, corners, and total shots are FT-only and not applicable because the data does not exist.
