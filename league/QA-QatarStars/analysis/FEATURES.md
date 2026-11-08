# Step 5 — Features: QA-QatarStars (J1 template X1–X9)

Causality contract as in the J1 template: features for match M use only
matches strictly before M; ratios are ratios of sums; NaN ⇒ the arm
needing the feature is inactive for that match, never silently filled.

| Feature | Verdict | Reason (measured in THIS league) |
|---|---|---|
| X1 blend pair (goals+xG) | **PARTIAL — goals-only** | No `expected_goals*` key in any of 714 payloads; no shotmap. The DC goals engine runs goals-only, the documented fallback. |
| X2 mover tier offset | **ADOPTED (goals only)** | 4 entrant transitions in dev (F4): GF −0.356, GA +0.360 vs league team mean; GA positive in 4/4, GF negative in 4/4 — a systematic entrant weakness, larger than FI/EC. Implemented as an ENTRANT arm on G-QA (offset for teams in their first season in the corpus, estimated on dev transitions, frozen in the prereg). |
| X3 set-play xG share | **DROPPED** | No xG at all in the feed (data absent). |
| X4 xG per shot | **DROPPED** | No shotmap in any season (0/714). S-QA has no X4 arm (and S-QA is not-buildable anyway). |
| X5 trailing target-rate means | **ADOPTED (goals only)** | Core of the goals engine; the goals target exists in all seasons and its trait is reliable (F2: split-half r 0.796). For S/C/K/T the targets do not exist in dev, so X5 has nothing to rate there. Implemented as Dixon-Coles attack/defence ratings (the goals-engine form of trailing target rates). |
| X6 xGOT per shot | **DROPPED** | No shotmap / no xGOT (data absent). |
| X7 opp-box touches | **DROPPED** | `touches_opp_box` exists only in the stats era (2025/2026+) — the same window as the corners target itself and outside dev — so a touches variant has no dev window to be evaluated on; C-QA is not-buildable on window grounds regardless. Dropped on window + absence-in-dev grounds. |
| X8 referee yellow rate | **DROPPED** | No referee field is populated in any dev match (0% coverage 2021/2022–2024/2025; named referees only 9/132 in 2025/2026). The trait cannot be measured on dev at all. K-QA is single-arm in any case — and not-buildable (no dev target). |
| X9 keeper saves / territorial covariates | **DROPPED (not used)** | `keeper_saves` and possession exist only in the stats era (2025/2026+); no dev window exists to measure a saves/possession trait or to evaluate a covariate arm. Recorded here so the omission is a decision, not an oversight. |

Halves constants (presentation only, frozen; source EDA F3):
goals **0.4385** from EVENT TIMES over the dev era 2021/2022–2024/2025
(1,749 goals, 505 matches). SOT / corners / total shots / yellows:
**no constant** — no period splits exist in the dev era (0 matches),
so no 1H share is computable or frozen for any count market.
