# Step 5 — Features: CH-ChallengeLeague (J1 template X1–X9)

Causality contract as in the J1 template: features for match M use only
matches strictly before M; ratios are ratios of sums; NaN ⇒ the arm
needing the feature is inactive for that match, never silently filled.

| Feature | Verdict | Reason (measured in THIS league) |
|---|---|---|
| X1 blend pair (goals+xG) | **PARTIAL — goals-only** | No `expected_goals*` key in any of 966 payloads; no shotmap. The DC goals engine runs goals-only, the documented fallback. |
| X2 mover tier offset | **DROPPED** | 7 entrant transitions measured in-corpus (F4): GF −0.079, GA −0.035 vs league team mean, mixed signs — no systematic tilt to estimate (contrast FI −0.210/+0.159). CH is tier 2; entrants mix relegated/promoted clubs. Dropped pre-fitting on EDA evidence. |
| X3 set-play xG share | **DROPPED** | No xG at all in the feed (data absent). |
| X4 xG per shot | **DROPPED** | No shotmap in any season (0/966). S-CH has no X4 arm. |
| X5 trailing target-rate means | **ADOPTED** | Core of every count engine here; targets exist (goals all seasons; SOT/corners/shots/yellows in the stats era 2023/2024+); traits reliable (F2: 0.62–0.80). Implemented as decay-weighted (HL 365d) for/against rates shrunk to the league mean with prior K = 8. |
| X6 xGOT per shot | **DROPPED** | No shotmap / no xGOT (data absent). |
| X7 opp-box touches | **DROPPED** | `touches_opp_box` exists only in the stats era — the same window as the corners target itself — so a touches variant has no extra dev window to be evaluated on beyond Gate Zero's own; and the corners candidate is single-arm by the FI precedent for feed-forced cases. Dropped on window grounds. |
| X8 referee yellow rate | **DROPPED** | No referee field exists in the payload structure parsed here; the trait cannot be measured at all. K-CH is single-arm. |
| X9 territorial covariates | **DROPPED (not used)** | Possession is present in every stats match (trait r 0.71), but the CH count engines are a deliberately minimal trait-rate port (see MODEL_DESIGN divergence note); no covariate arm is pre-registered, so nothing is fitted post-hoc. Recorded here so the omission is a decision, not an oversight. |

Halves constants (presentation only, frozen; source EDA F3):
goals 0.4409 from EVENT TIMES over the dev era 2021/2022–2024/2025
(2,207 goals); SOT 0.4512, corners 0.4800, total shots 0.4467,
yellows 0.3399 from PERIOD SPLITS over the dev stats era
2023/2024–2024/2025 (n=360 matches).
