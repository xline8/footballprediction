# Step 5 — Features: FI-Veikkausliiga (J1 template X1–X9)

Causality contract as in the J1 template: features for match M use only
matches strictly before M; ratios are ratios of sums; NaN ⇒ the arm needing
the feature is inactive for that match, never silently filled.

| Feature | Verdict | Reason (measured in THIS league) |
|---|---|---|
| X1 blend pair (goals+xG) | **PARTIAL — goals-only** | No `expected_goals*` key in any of 1,017 payloads (not even the rich 2025–26 era); no shotmap. The DC reference runs goals-only, its documented fallback. |
| X2 mover tier offset | **ADOPTED (goals arm)** | 8 entrant transitions measured in-corpus (F4): GF −0.210, GA +0.159 vs league team mean — promoted-team pattern, same sign as J1 F4. FI is tier 1: entrants are promoted clubs, identified by absence from the previous Veikkausliiga season (no tier-2 corpus is built in-system; the offset itself is estimated inside the fit from completed transitions only). |
| X3 set-play xG share | **DROPPED** | No xG at all in the feed (data absent). |
| X4 xG per shot | **DROPPED** | No shotmap in any season (0/1,017). S-FI therefore has no X4 arm. |
| X5 trailing target-rate means | **ADOPTED** | Part of the reference architectures; targets exist (SOT/corners 2021+, yellows all seasons via events); traits reliable (F2: SOT 0.532, corners 0.708, yellows 0.778). |
| X6 xGOT per shot | **DROPPED** | No shotmap / no xGOT (data absent). |
| X7 opp-box touches | **DROPPED** | `touches_opp_box` exists ONLY in 2025–2026 (531 of 1,017 period rows per period; zero before 2025). Its trait is reliable where measured (2025-only r = 0.835), but a corners variant arm needs trailing touches across the dev walk-forward (2022–2025): the feature is NaN for 2022–2024 and most of 2025, so the arm cannot be dev-evaluated. Dropped on window grounds, not trait grounds. C-FI is a single-arm (Gate Zero) candidate. |
| X8 referee yellow rate | **DROPPED** | Referee name empty in 885/1,017 payloads and in ALL of 2021–2024; named 36/177 (2025), 96/177 (2026). The trait cannot be measured on the dev era. K-FI is a single-arm (Gate Zero) candidate. |
| X9 reference territorial covariates | **PARTIAL — possession only** | `big_chance` exists only 2025–2026 (same window problem as X7); `BallPossesion` is present in every stats match (trait r = 0.898). Gate Zero corners runs with the possession covariate only — a feed-forced divergence from production corners_v3, recorded here and in PREREG_C_FI (identical to the SE2 ruling). |

Halves constants (presentation only, frozen; source in EDA F3):
goals 0.4295 and yellows 0.3109 from EVENT TIMES over the dev era
2021–2025; SOT 0.4400 and corners 0.4631 from the 2025 PERIOD SPLITS
(the only dev season that has them). Total shots: no constant — T-FI is
not built (target definition break, MODEL_DESIGN).
