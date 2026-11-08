# Step 4/5 — Features: MA-BotolaPro (J1 X1–X9 template)

Causality contract as in J1 FEATURES (strictly pre-match inputs,
trailing windows, ratio-of-sums, NaN ⇒ arm inactive, never filled).

| # | Feature | Verdict | Reason (this league's data) |
|---|---|---|---|
| X1 | Blend pair (goals, xG) | **DROPPED** | No xG key exists in any of the 1,255 payloads. Goals fit is goals-only. |
| X2 | Mover tier offset | **DROPPED** | Botola 2 is not in the warehouse (Morocco = 1 league in the index); neighbour-tier membership unobservable. The entrant problem it addresses is instead covered by the sanctioned SHRINK arm (EDA entrant gaps ΔGF −0.107 / ΔGA +0.283, n=6). |
| X3 | Set-play xG share | **DROPPED** | No xG at all (X1). |
| X4 | xG per shot | **DROPPED** | No shotmap in any payload (0/1,255). |
| X5 | Trailing target-rate means (naive/ensemble) | **ADOPTED** | The count targets exist in the rich era; split-half r: SOT 0.40/0.45, corners 0.60/0.43, shots 0.65/0.51. For yellows, for-trait r=0.010 (NOISE) / against 0.310 — adopted as the reference architecture's own component, with the weakness recorded; the gate decides. |
| X6 | xGOT per shot | **DROPPED** | No shotmap / xGOT anywhere. |
| X7 | Opp-box touches | **DROPPED** | `touches_opp_box` key absent from the four-key stats feed. |
| X8 | Referee yellow rate | **DROPPED** | Referee text empty in 1,255/1,255 payloads — no referee identity exists in this league's data at all. |
| X9 | Territorial covariates (possession + big chance) | **PARTIALLY ADOPTED (possession only)** | `BallPossesion` exists in the rich era (trait r=0.608); `big_chance` is absent from the feed entirely. Corners Gate Zero is the production pattern with the possession-only multiplier (SCO-Championship precedent). |

## Halves constants (frozen, presentation only)

- goals_1h_share **0.4274** (goal-event times, dev seasons; true
  per-match share variance = 0).
- yellow_cards_1h_share **0.3465** (card-event times, rich dev era).
- SOT / corners / total shots: **null** — no legitimate halves
  source exists; FT presentation only.

## Rejected (J1 §3 carried over)

Per-team/per-match half shares (true variance 0 for goals), trailing
finishing/conversion (no xG), on-target rate as a standalone
covariate, lineup/absence features, standings/h2h snapshots
(leakage), attendance (not pre-match), red-card rates as a target.
