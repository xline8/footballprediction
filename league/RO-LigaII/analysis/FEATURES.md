# Step 5 — Feature Engineering (J1 template X1–X9, judged on RO-LigaII)

The global causality contract is inherited from J1: features use only strictly pre-match observations, trailing/expanding windows, ratio-of-sums where applicable, and NaN means an arm is inactive. Ratings and home advantage are fitted architectural components, not extra covariates.

| # | Feature | RO-LigaII verdict | Evidence |
|---|---|---|---|
| X1 | Blend observation pair (goals + xG) | **ADOPTED, goals-only form** | xG and shotmap are absent in 1,513/1,513 files. |
| X2 | Mover tier offset | **DROPPED** | No inter-league Liga I→Liga II matches calibrate an offset. Promoted-team risk is covered by the sanctioned goals SHRINK arm. |
| X3 | Set-play xG share/rate | **DROPPED** | No xG source or split exists. |
| X4 | xG per shot | **DROPPED** | Shotmap contains 0 shots in 1,513 files. |
| X5 | Trailing target-rate means | **ADOPTED in goals-only form** | Trailing goal-rate means are the Dixon–Coles ratings observations; goals-for split-half r=0.411. |
| X6 | Attacking xGOT/shot | **DROPPED** | No xGOT or shotmap source. |
| X7 | Opp-box touches | **DROPPED** | No stats feed at all. |
| X8 | Referee yellow rate | **DROPPED** | Referee is blank in all 1,513 files. |
| X9 | Territorial covariates | **DROPPED** | No possession, box-touch or other stats covariate exists. |

## Rejected items

- Team first-half shares: **NOISE**; the frozen goals constant is presentation-only and per-match shares are not stable team traits.
- Red cards as a target: **REJECTED**; only 148 Red and 106 YellowRed events exist, making this a rare-event count, not a supported market target.
- Phase as a model input: **REJECTED**; it is an audit/inclusion field, not a causal pre-match feature.
- Standings and H2H: **LEAKAGE** in the payload snapshots.
- Lineup/absence: **CLOSED** programme-wide.
