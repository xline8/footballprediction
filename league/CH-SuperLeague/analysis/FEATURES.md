# Phase 3.5 — Feature Engineering (J1 template X1–X9, judged on CH data)

Consumption rule and causality contract are inherited verbatim from
`league/J1/analysis/FEATURES.md` (trailing/expanding windows only,
strictly pre-match, ratio-of-sums, NaN ⇒ arm inactive, never
imputed). Only the verdicts differ — each was re-measured on this
league (EDA).

| # | Feature (J1 analogue) | CH verdict | Evidence |
|---|---|---|---|
| X1 | Blend observation pair (goals + xG) | **ADOPTED** | xG in 1,121/1,122 matches from 2021/2022 (one goals-only fallback); F11 goals/xG ≈ 1.04 pooled |
| X2 | Mover tier offset | **DROPPED** | No feeder tier in corpus (F4) — the offset is not estimable. Replaced in the goals design by the SHRINK thin-data arm (sanctioned G-J2 lesson), an architectural prior, not X2 |
| X3 | Set-play xG share/rate (trailing) | **ADOPTED** (arm) | F5 split-half r=0.369 — weak-moderate; arm status only, gate decides |
| X4 | xG per shot (trailing) | **DROPPED** | F6 r=0.247 — below the arm standard (DK adopted at 0.348); on-target rate is noise (−0.121). S-CH runs Gate Zero + RS only |
| X5 | Trailing target-rate means (naive/ensemble) | **ADOPTED** | F2: shots 0.937, SOT 0.875, corners 0.795 reliable; yellows 0.256 weak — the naive baseline is still defined identically, the gate decides |
| X6 | Attacking xGOT/shot (era-guarded) | **DROPPED** | F7: era-guarded (2024/2025+) split-half r=0.212 — fails the reliability standard (J1 0.518; DK dropped at the same 0.212). Not built |
| X7 | Opp-box touches for/against (trailing) | **ADOPTED** (arm) | F9: r=0.933 for / 0.835 against — the strongest traits in this EDA. Coverage 68–86% in 2021/2022–2023/2024, 100% from 2024/2025 — the min-8 rule absorbs the early gaps; arm inactive where the window cannot fill |
| X8 | Referee yellow rate (trailing) | **ADOPTED** (arm) | F8: r=0.549, 15 referees ≥20 matches. Coverage 47.2% in 2021/2022 → ~100% from 2023/2024; early dev values are often the shrunk league mean. Same operational caveat as J1: no published appointment ⇒ base arm, no imputation |
| X9 | Reference territorial covariates (possession, big chances) | **ADOPTED** (Gate Zero) | F9: possession r=0.920, big-chance r=0.811 in CH |

## Rejected (inherited from J1 §3, re-affirmed on CH data)

- Team half shares (all stats): NOISE (F3) — frozen constants only:
  goals 0.437, SOT 0.453, corners 0.471, shots 0.456, yellows 0.357.
- Trailing finishing, trailing conversion, standalone on-target rate
  as a covariate (r=−0.121, noise; v5's internal Beta-Binomial ratio
  component is an architectural component, and the RS arm tests its
  shrinkage — the covariate itself stays out).
- Defensive xGOT (never measured as signal anywhere; X6 dropped whole).
- Lineup/absence (CLOSED, F10), standings/h2h snapshots (leakage),
  attendance (not pre-match), red cards as target (rare-event count).
- Any phase (regular/split) feature: the split flag is a
  preprocessing record, not a model input (MODEL_DESIGN rule).
