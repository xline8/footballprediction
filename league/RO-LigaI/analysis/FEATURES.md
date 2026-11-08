# Step 5 — Feature Engineering (J1 template X1–X9, judged on RO data)

Consumption rule and causality contract inherited verbatim from
`league/J1/analysis/FEATURES.md` (trailing/expanding windows only,
strictly pre-match, ratio-of-sums, NaN ⇒ arm inactive, never
imputed). Verdicts re-measured on this league (EDA).

| # | Feature (J1 analogue) | RO verdict | Evidence |
|---|---|---|---|
| X1 | Blend observation pair (goals + xG) | **ADOPTED, goals-only form** | xG never published for id 189 (0/1,701 matches); the reference blend's documented goals-only fallback is the whole model here |
| X2 | Mover tier offset | **DROPPED** | Feeder tier (Liga II) is a separate warehouse league, not part of this build — offset not estimable (CH precedent). Promoted-team risk is covered by the goals SHRINK arm instead |
| X3 | Set-play xG share/rate | **DROPPED** | No xG splits exist (data absent) |
| X4 | xG per shot | **DROPPED** | Shotmap holds zero shots in all 1,701 matches (data absent) |
| X5 | Trailing target-rate means (naive/ensemble) | **ADOPTED** | F2: shots-for r=0.831, SOT-for 0.611, corners-for 0.439 reliable; yellows-for 0.237 weak but the naive baseline is defined identically — the gate decides |
| X6 | Attacking xGOT/shot | **DROPPED** | No shotmap/xGOT (data absent) |
| X7 | Opp-box touches for/against | **DROPPED** | `touches_opp_box` published only from 2025/2026 — zero dev-era observations; a variant arm could never be dev-tested |
| X8 | Referee yellow rate (trailing) | **ADOPTED** (arm) | F8: r=0.568, 22 referees ≥20 matches, coverage 99.4%. Same caveat as J1: no published appointment ⇒ base arm |
| X9 | Reference territorial covariates | **ADOPTED in reduced form** (Gate Zero) | Possession r=0.766, available all eras. Big chances exist only 2025/2026+ → excluded from the corners Gate Zero covariate set (documented divergence from the CH/J1 reference, forced by the feed) |

## Rejected (inherited from J1 §3, re-affirmed on RO data)

- Team half shares: NOISE — frozen constants only (goals 0.453,
  SOT 0.455, corners 0.477, shots 0.459, yellows 0.330; EDA F3).
- Trailing finishing / conversion as standalone covariates;
  on-target rate as a standalone covariate (it lives inside the
  v5 SOT architecture's ratio component, and its shrinkage is what
  the RS arm tests).
- Defensive xGOT (no data), lineup/absence (CLOSED, F10),
  standings/h2h snapshots (leakage), attendance (not pre-match),
  red cards as a target (rare-event count).
- Any phase (regular/championship/relegation) feature: the phase
  flag is a preprocessing record, not a model input.
- Raw total shots as a cross-era target (definition break, F1).
