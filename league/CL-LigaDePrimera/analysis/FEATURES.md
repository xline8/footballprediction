# Step 5 — Features — CL-LigaDePrimera (J1 template X1–X9)

Global causality contract as in the J1 FEATURES.md §0 (strictly
pre-match inputs, trailing windows or expanding-with-decay fits,
ratios of sums, NaN ⇒ arm inactive, never silently filled). Only
features listed ADOPTED here may enter MODEL_DESIGN.

| # | J1 analogue | Verdict | Reason (this league's evidence) |
|---|---|---|---|
| X1 | Blend observation pair (goals + xG) | **DROPPED** | `expected_goals` present in 0 of 1,448 payloads; no shotmap in any season. Goals model is goals-only; there is no blend pair to build. |
| X2 | Mover tier offset | **DROPPED** | No Chile tier-2 corpus exists in the warehouse index (league 273 is the only Chile competition), so no tier step can be estimated. The sanctioned SHRINK prediction-time shrinkage is still registered as a goals arm (G-J2 lesson) — it needs no cross-tier data. |
| X3 | Set-play xG share/rate | **DROPPED** | No xG, hence no set-play split (see X1). |
| X4 | xG per shot | **DROPPED** | No shotmap in any season. |
| X5 | Trailing target-rate means (naive/ensemble inputs) | **ADOPTED** | All targets reliable at team-season scale: SOT r 0.315/0.357, corners 0.333/0.320, total shots 0.407/0.523, event yellows 0.315 (EDA). Consumed by the SOT/corners/cards/total-shots reference architectures exactly as in production. |
| X6 | Attacking xGOT per shot | **DROPPED** | No shotmap / xGOT exists. |
| X7 | Box touches (corners multiplier input) | **ADOPTED** | `touches_opp_box` present in the stats feed across the era; split-half reliability r = 0.432 (for). Registered as the corners variant arm (box-touch multiplier, the production C-family pattern). |
| X8 | Referee covariate (cards) | **DROPPED** | Referee strictness split-half r = 0.357 — weak — and referee identity is missing for 100% of the 2021 warm-up season and 4–26% of later seasons, so the covariate cannot be carried through the walk-forward honestly. Not registered as an arm. |
| X9 | Territory/possession multiplier inside corners Gate Zero | **ADOPTED (as reference-internal)** | Part of the unmodified production corners pattern (possession z-multiplier); retained exactly as the reference defines it. |

## Halves constants (frozen, presentation only)

goals 0.4400 · SOT 0.4456 · corners 0.4644 · total shots 0.4535 ·
yellow cards 0.3818. Sources and noise tests in EDA. Every market
has a legitimate halves source (goal-event times for goals;
2023+ period splits for the rest), so **no market is FT-only** in
this league — with the recorded caveat that the splits-based
constants describe the 2023+ era and are applied as frozen
presentation constants, per program rule.
