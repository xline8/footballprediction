# Step 5 — Features — CL-LigaDeAscenso (J1 template X1–X9)

Global causality contract as in the J1 FEATURES.md §0 (strictly
pre-match inputs, trailing windows or expanding-with-decay fits,
ratios of sums, NaN ⇒ arm inactive, never silently filled). Only
features listed ADOPTED here may enter MODEL_DESIGN.

| # | J1 analogue | Verdict | Reason (this league's evidence) |
|---|---|---|---|
| X1 | Blend observation pair (goals + xG) | **DROPPED** | `expected_goals` present in 0 of 1,515 payloads; shotmap empty in every payload. Goals model is goals-only; no blend pair exists. |
| X2 | Mover tier offset | **ADOPTED** | Parent tier CL-LigaDePrimera corpus exists (league 273, built). Exactly 2 relegated teams join per season — 8 mover team-seasons across the dev+virgin span (2022–2025), each with a full prior Primera season (~30 matches) in the parent corpus. Registered as a goals arm with the DK-1Division transplant definition (parent-DC ratings blended for arriving teams with <12 in-league training matches, weight from the parent match count). Estimated only from prior-tier data, never hard-coded. |
| X3 | Set-play xG share/rate | **DROPPED** | No xG, hence no set-play split (see X1). |
| X4 | xG per shot | **DROPPED** | No shotmap in any season. |
| X5 | Trailing target-rate means (naive/ensemble inputs) | **DROPPED** | Its consumers are the SOT/corners/cards/total-shots architectures, and none of those targets exists in this league (stats content = 0 rows; cards target era-less, DATA_UNDERSTANDING). Reliability is not computable for any stats trait (n = 0 team-seasons). Goals traits are weak (for r = 0.198, against r = 0.241) and are consumed by the DC reference itself, not by an X5 arm. |
| X6 | Attacking xGOT per shot | **DROPPED** | No shotmap / xGOT exists. |
| X7 | Box touches (corners multiplier input) | **DROPPED** | `touches_opp_box` lives in the stats block, which is an empty shell in every payload (0 rows). Corners are not buildable regardless. |
| X8 | Referee covariate (cards) | **DROPPED** | Referee identity absent on 100% of dev-era matches (0/1,030 in 2021–2024; 54 in 2025, 2 in 2026). No strictness reliability is computable, and cards are not buildable regardless. |
| X9 | Territory/possession multiplier inside corners Gate Zero | **DROPPED** | Possession lives in the (empty) stats block; corners are not buildable. |

## Halves constants (frozen, presentation only)

goals **0.4273** (goal-event times, dev era 2022–2024,
goal-events-complete matches; true per-match share variance = 0 —
EDA). All other markets: **FT-only** (`halves_share_1h: null`) —
no legitimate halves source exists in this league's data (no
period splits anywhere; the stats block is empty). This is the
RU-1Division-style configuration the runner already supports.
