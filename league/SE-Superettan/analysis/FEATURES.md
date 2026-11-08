# Step 5 — Features: SE-Superettan (J1 template X1–X9)

Causality contract as in the J1/SE template: features for match M use only
matches strictly before M; ratios are ratios of sums; NaN ⇒ the arm needing
the feature is inactive for that match, never silently filled.

| Feature | Verdict | Reason (measured in THIS league) |
|---|---|---|
| X1 blend pair (goals+xG) | **PARTIAL — goals-only** | xG keys absent in all 1,440 payloads; the DC reference runs goals-only, its documented fallback. |
| X2 mover tier offset | **ADOPTED (goals arm)** | Parent Allsvenskan corpus exists in-system. 12 relegated-entrant transitions measured (F4): GF +0.117, GA −0.192 vs league team mean. Offset estimated inside each fit from transitions completed before the predicted season; promoted-from-Division-1 entrants (13) have no corpus and take no offset. |
| X3 set-play xG share | **DROPPED** | No xG at all in the feed (data absent). |
| X4 xG per shot | **DROPPED** | No shotmap in any season (0/1,440). S-SE2 therefore has no X4 arm. |
| X5 trailing target-rate means | **ADOPTED** | Part of the reference architectures; targets exist (SOT/corners/shots 2022+, yellows all seasons via events); traits reliable (F2). |
| X6 xGOT per shot | **DROPPED** | No shotmap / no xGOT (data absent). |
| X7 opp-box touches | **DROPPED** | `touches_opp_box` key absent in all 1,440 payloads. C-SE2 is a single-arm (Gate Zero) candidate. |
| X8 referee yellow rate | **DROPPED** | Referee name empty in 1,440/1,440 payloads — the trait cannot even be measured. K-SE2 is a single-arm (Gate Zero) candidate. |
| X9 reference territorial covariates | **PARTIAL — possession only** | `big_chance` absent everywhere; `BallPossesion` present in every stats match (trait r = 0.605). Gate Zero corners runs with the possession covariate only — a feed-forced divergence from production corners_v3, recorded here and in PREREG_C_SE2. |

Halves constants (presentation only, frozen): goals 0.4317, yellows 0.3344
(from event times, dev era). SOT/corners/total shots: **FT-only** (null shares).
