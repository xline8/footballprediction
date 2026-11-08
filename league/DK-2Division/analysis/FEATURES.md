# Feature decisions — DK-2Division

| Feature | Verdict | Evidence |
|---|---|---|
| X1 goals + xG observation blend | **DROPPED** | no xG in any of 1,050 payloads |
| X2 mover tier offset | **ADOPTED** | 10 mover team-seasons, 2/season, prior-tier matches in warehouse; ratings transplanted from a parent-tier DC fit under the frozen weight formula in MODEL_DESIGN, never hard-coded as a constant |
| X3 set-play xG share | **DROPPED** | no xG |
| X4 xG per shot | **DROPPED** | shotmap empty (0 shots) |
| X5 trailing target-rate means | **NOT A SEPARATE ARM for goals** | DC ratings are trailing goal-based; no SOT/corners/cards target exists for X5 |
| X6 xGOT/shot | **DROPPED** | no shotmap/xGOT |
| X7 opp-box touches | **DROPPED** | no stats feed |
| X8 referee yellow rate | **DROPPED** | referee text empty in 1,050/1,050 and no cards target |
| X9 possession/big-chance covariates | **DROPPED** | no stats feed |

Frozen presentation constant: `goals_1h_share: 0.4611`. Rejected items: R1 team half-shares are noise (r=−0.120); R12 reds as a target are rare-event counts (about 0.08–0.11/match), events-only.
