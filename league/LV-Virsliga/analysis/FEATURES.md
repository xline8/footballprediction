# Step 4/5 — Features: LV-Virsliga (J1 X1–X9 template)

Causality contract as in J1 FEATURES (strictly pre-match inputs,
trailing windows, ratio-of-sums, NaN ⇒ arm inactive, never filled).

| # | Feature | Verdict | Reason (this league's data) |
|---|---|---|---|
| X1 | Blend pair (goals, xG) | **DROPPED** | No xG key exists in any of the 1,017 payloads; no shotmap anywhere. Goals fit is goals-only. |
| X2 | Mover tier offset | **DROPPED** | Latvia has exactly one league in the warehouse (Virsliga 226); neighbour-tier membership unobservable. The entrant problem it addresses is instead covered by the sanctioned SHRINK arm (EDA entrant gaps ΔGF −0.453 / ΔGA +0.255, n=6). |
| X3 | Set-play xG share | **DROPPED** | No xG at all (X1). |
| X4 | xG per shot | **DROPPED** | No shotmap in any payload (0/1,017). |
| X5 | Trailing target-rate means (naive/ensemble) | **ADOPTED** | The count targets exist in the stats era; split-half r: SOT 0.89/0.88, corners 0.69/0.62, shots 0.90/0.87, yellows (events) 0.60/0.58. |
| X6 | xGOT per shot | **DROPPED** | No shotmap / xGOT anywhere. |
| X7 | Opp-box touches | **DROPPED** | `touches_opp_box` key absent from all 1,017 payloads. |
| X8 | Referee yellow rate | **DROPPED** | Referee populated in only 40/180 (2025) and 55/179 (2026) matches; ~12 referees with 1–5 matches each in 2025 — no rate estimable, and 78% of matches have no referee at all. |
| X9 | Territorial covariates (possession + big chance) | **PARTIALLY ADOPTED (possession only)** | `BallPossesion` exists in the stats era (trait r=0.906); `big_chance` is identically 0 in all 359 stats-era matches — the key exists but the feed never populates it. Corners Gate Zero is the production pattern with the possession-only multiplier (SCO-Championship precedent). |

## Halves constants (frozen, presentation only — all from 2025)

- goals_1h_share **0.4569** (goal-event times; true per-match share variance = 0).
- sot_1h_share **0.4637** (period splits).
- corners_1h_share **0.4816** (period splits).
- total_shots_1h_share **0.4685** (period splits).
- yellow_cards_1h_share **0.3306** (card-event times).

## Rejected (J1 §3 carried over)

Per-team/per-match half shares (true variance 0 for every
market), trailing finishing/conversion (no xG), on-target rate as
a standalone covariate, lineup/absence features, standings/h2h
snapshots (leakage), attendance (not pre-match), red-card rates
as a target. Stats `yellow_cards` as a target (feed hole: 43/180
zeroed matches in 2025 — the event feed is the target instead).
