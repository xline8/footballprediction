# Phase A — Feature Decisions: SCO Championship

The consumption contract is strictly pre-match trailing/expanding windows; NaN means the arm is inactive and is never imputed.

| # | Feature | Verdict | Evidence / decision |
|---|---|---|---|
| X1 | Goals + xG blend | **DROPPED** | No xG in 969 matches. |
| X2 | Mover tier offset | **ADOPTED (arm)** | Premiership entrants: ΔGF +0.3875, ΔGA −0.4077; League One entrants: +0.0160/+0.0646. Estimate in fit per the PREREG_G_DE2 pattern. |
| X3 | Set-play xG | **DROPPED** | No xG. |
| X4 | Shotmap-derived features | **DROPPED** | No shotmap. |
| X5 | Trailing target-rate means | **ADOPTED** | Reliability evidence: use measured r values. |
| X6 | xGOT | **DROPPED** | No xGOT. |
| X7 | Opponent-box touches | **DROPPED** | Present in only 19 rich matches. |
| X8 | Referee yellow rate | **DROPPED** | r=0.3318, below the ~0.45+ adoption standard; SCO-Prem r=0.158, J1 adopted at 0.65. K runs Gate Zero only. |
| X9 | Possession / big chance territory | **ADOPTED (possession-only)** | Possession r=0.6383; big chance is absent except in 19 rich matches, so it is omitted. Used for corners Gate Zero only. |

Frozen halves constants are goals 0.4553 and `yellow_cards` 0.3121. SOT, corners, and total shots are FT-only (`null`).
