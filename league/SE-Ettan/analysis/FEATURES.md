# Step 5 — Features: SE-Ettan (J1 template X1–X9)

Causality contract as in the J1 template: features for match M use only
matches strictly before M; ratios are ratios of sums; NaN ⇒ the arm
needing the feature is inactive for that match, never silently filled.

| Feature | Verdict | Reason (measured in THIS league) |
|---|---|---|
| X1 blend pair (goals+xG) | **PARTIAL — goals-only** | No `expected_goals*` key in any of 2,880 payloads; no shotmap. The DC goals engine runs goals-only, the documented fallback. |
| X2 mover tier offset | **REJECTED** | 27 entrant transitions in dev (F4): GF −0.013, GA +0.081 vs league team mean; GF negative in 13/27, GA positive in 15/27; per-season signs flip. No systematic entrant weakness — entrants mix strong relegated Superettan sides with weak promoted Division 2 sides. No ENTRANT arm on G-SE. |
| X3 set-play xG share | **DROPPED** | No xG at all in the feed (data absent). |
| X4 xG per shot | **DROPPED** | No shotmap in any season (0/2,880). S-SE has no X4 arm (and S-SE is not-buildable anyway). |
| X5 trailing target-rate means | **ADOPTED (goals only)** | Core of the goals engine; the goals target exists in all seasons and its trait is reliable (F2: split-half r 0.562 dev / 0.703 scored window for goals-for; 0.742 / 0.604 for goals-against). For S/C/K/T the targets do not exist in any season, so X5 has nothing to rate there. Implemented as Dixon-Coles attack/defence ratings (the goals-engine form of trailing target rates). |
| X6 xGOT per shot | **DROPPED** | No shotmap / no xGOT (data absent). |
| X7 opp-box touches | **DROPPED** | `touches_opp_box` exists nowhere — there is no stats feed in any season. C-SE is not-buildable on window grounds regardless. Dropped on absence grounds. |
| X8 referee yellow rate | **DROPPED** | No referee field is populated in any match (0% coverage 2021–2025; 0 distinct referees in the raw scan). The trait cannot be measured at all. K-SE is not-buildable in any case (see F5). |
| X9 keeper saves / territorial covariates | **DROPPED (not used)** | `keeper_saves` and possession exist nowhere (no stats feed in any season); no window exists to measure a saves/possession trait or to evaluate a covariate arm. Recorded here so the omission is a decision, not an oversight. |

Halves constants (presentation only, frozen; source EDA F3):
goals **0.4385** from EVENT TIMES over the dev era 2022–2024
(1,885 goals, 1,439 matches; 2021 has no events; awarded match
4398485 excluded). SOT / corners / total shots / yellows:
**no constant** — no period splits exist in any season (0 matches),
so no 1H share is computable or frozen for any count market.
Event-time 1H yellows (0.2841, 1,375 of 4,840, 2022–2024) are
descriptive evidence for a possible future K decision only — not a
frozen constant for any built market.
