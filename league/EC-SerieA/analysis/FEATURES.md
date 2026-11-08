# Step 5 — Features: EC-SerieA (J1 template X1–X9)

Causality contract as in the J1 template: features for match M use only
matches strictly before M; ratios are ratios of sums; NaN ⇒ the arm
needing the feature is inactive for that match, never silently filled.

| Feature | Verdict | Reason (measured in THIS league) |
|---|---|---|
| X1 blend pair (goals+xG) | **PARTIAL — goals-only** | No `expected_goals*` key in any of 1,565 payloads; no shotmap. The DC goals engine runs goals-only, the documented fallback. |
| X2 mover tier offset | **ADOPTED (goals only)** | 6 entrant transitions in dev (F4): GF −0.121, GA +0.263 vs league team mean; GA positive in 6/6, GF negative in 5/6 — a systematic entrant weakness of FI-like size. Implemented as an ENTRANT arm on G-EC (offset for teams in their first season in the corpus, estimated on dev transitions, frozen in the prereg). |
| X3 set-play xG share | **DROPPED** | No xG at all in the feed (data absent). |
| X4 xG per shot | **DROPPED** | No shotmap in any season (0/1,565). S-EC has no X4 arm (and S-EC is not-buildable anyway). |
| X5 trailing target-rate means | **ADOPTED (goals only)** | Core of the goals engine; the goals target exists in all seasons and its trait is reliable (F2: split-half r 0.75). For S/C/K/T the targets do not exist in dev, so X5 has nothing to rate there. Implemented as Dixon-Coles attack/defence ratings (the goals-engine form of trailing target rates). |
| X6 xGOT per shot | **DROPPED** | No shotmap / no xGOT (data absent). |
| X7 opp-box touches | **DROPPED** | `touches_opp_box` exists only in the stats era (2025+) — the same window as the corners target itself and outside dev — so a touches variant has no dev window to be evaluated on; C-EC is not-buildable on window grounds regardless. Dropped on window + absence-in-dev grounds. |
| X8 referee yellow rate | **DROPPED** | No referee field is populated in any dev match (0% coverage 2021–2024; named referees only from 2025, 73/312). The trait cannot be measured on dev at all. K-EC is single-arm in any case — and not-buildable (no dev target). |
| X9 keeper saves / territorial covariates | **DROPPED (not used)** | `keeper_saves` and possession exist only in the stats era (2025+); no dev window exists to measure a saves/possession trait or to evaluate a covariate arm. Recorded here so the omission is a decision, not an oversight. |

Halves constants (presentation only, frozen; source EDA F3):
goals **0.4616** from EVENT TIMES over the dev era 2021–2024
(2,474 goals, 902 matches). SOT / corners / total shots / yellows:
**no constant** — no period splits exist in the dev era (0 matches),
so no 1H share is computable or frozen for any count market.
