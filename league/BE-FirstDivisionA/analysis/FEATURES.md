# Phase 3.5 — Feature Engineering (J1 template X1–X9, judged on BE data)

Consumption rule and causality contract are inherited verbatim from
`league/J1/analysis/FEATURES.md` (trailing/expanding windows only,
strictly pre-match, ratio-of-sums, NaN ⇒ arm inactive, never
imputed). Only the verdicts differ — each was re-measured on this
league (EDA).

| # | Feature (J1 analogue) | BE verdict | Evidence |
|---|---|---|---|
| X1 | Blend observation pair (goals + xG) | **ADOPTED** | xG in 1,695/1,698 matches from 2021/2022 (three goals-only fallbacks); F12 goals/xG ≈ 0.97 pooled, 0.92–1.08 per season |
| X2 | Mover tier offset | **DROPPED** | No feeder tier in corpus (F5) — the offset is not estimable. Replaced in the goals design by the SHRINK thin-data arm (sanctioned G-J2 lesson), an architectural prior, not X2 |
| X3 | Set-play xG share/rate (trailing) | **ADOPTED** (arm) | F6 split-half r=0.599 — strong; arm status only, gate decides |
| X4 | xG per shot (trailing) | **ADOPTED** (arm) | F7 r=0.435 — above the arm standard (DK adopted at 0.348; CH dropped at 0.247). S-BE runs Gate Zero + RS + X4, as S-DK did |
| X5 | Trailing target-rate means (naive/ensemble) | **ADOPTED** | F2: shots 0.886, SOT 0.866, corners 0.721 reliable; yellows 0.404 moderate — the naive baseline is still defined identically, the gate decides |
| X6 | Attacking xGOT/shot (era-guarded) | **DROPPED** | F8: era-guarded (2024/2025+) split-half r=0.075 — pure noise, the weakest xGOT reading in the program. Not built |
| X7 | Opp-box touches for/against (trailing) | **ADOPTED** (arm) | F10: r=0.916 for / 0.824 against — among the strongest traits in this EDA. Coverage 70–81% in 2021/2022–2023/2024, 100% from 2024/2025 — the min-8 rule absorbs the early gaps; arm inactive where the window cannot fill |
| X8 | Referee yellow rate (trailing) | **ADOPTED** (arm) | F9: r=0.378, 19 referees ≥20 matches — the weakest adopted X8 reading in the program (J1 0.646, DK 0.561, CH 0.549); arm status only. Coverage 41.2% in 2021/2022 → 93–100% from 2022/2023; early dev values are often the shrunk league mean. Same operational caveat as J1: no published appointment ⇒ base arm, no imputation |
| X9 | Reference territorial covariates (possession, big chances) | **ADOPTED** (Gate Zero) | F10: possession r=0.933, big-chance r=0.841 in BE |

## Rejected (inherited from J1 §3, re-affirmed on BE data)

- Team half shares (all stats): NOISE (F3) — frozen constants only:
  goals 0.458, SOT 0.452, corners 0.471, shots 0.456, yellows 0.317.
- Trailing finishing, trailing conversion, standalone on-target rate
  as a covariate (r=0.534 — reliable in BE, F7, but rejected per the
  J1 template: v5's internal Beta-Binomial ratio component is an
  architectural component, and the RS arm tests its shrinkage — the
  covariate itself stays out).
- Defensive xGOT (never measured as signal anywhere; X6 dropped whole).
- Lineup/absence (CLOSED, F11), standings/h2h snapshots (leakage),
  attendance (not pre-match), red cards as target (rare-event count).
- Any phase (regular/play-off group) feature: the phase flag is a
  preprocessing record and the inclusion decision is frozen
  (DATA_UNDERSTANDING §1); phase is never a model input.
