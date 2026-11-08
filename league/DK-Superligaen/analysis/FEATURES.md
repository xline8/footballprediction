# Phase 3.5 — Feature Engineering (J1 template X1–X9, judged on DK data)

Consumption rule and causality contract are inherited verbatim from
`league/J1/analysis/FEATURES.md` (trailing/expanding windows only,
strictly pre-match, ratio-of-sums, NaN ⇒ arm inactive, never imputed).
Only the verdicts differ — each was re-measured on this league (EDA).

| # | Feature (J1 analogue) | DK verdict | Evidence |
|---|---|---|---|
| X1 | Blend observation pair (goals + xG) | **ADOPTED** | xG in 100% of matches from 2021/2022; F11 calibration 0.997 pooled |
| X2 | Mover tier offset | **DROPPED** | No feeder tier in corpus (F4) — the offset is not estimable. Replaced in the goals design by the SHRINK thin-data arm (sanctioned G-J2 lesson), which is an architectural prior, not X2 |
| X3 | Set-play xG share/rate (trailing) | **ADOPTED** (arm) | F5 split-half r=0.567 |
| X4 | xG per shot (trailing) | **ADOPTED** (arm) | F6 r=0.348 — weak-moderate; arm status only, gate decides |
| X5 | Trailing target-rate means (naive/ensemble) | **ADOPTED** | F2: SOT 0.801, corners 0.605, yellows 0.599, shots 0.824 |
| X6 | Attacking xGOT/shot (era-guarded) | **DROPPED** | F7: era-guarded (2024/2025+) split-half r=0.212 — fails the reliability standard J1 set (0.518). Not built |
| X7 | Opp-box touches for/against (trailing) | **ADOPTED** (arm) | F9: r=0.830 for / 0.871 against. Coverage 60–74% in 2021/2022–2023/2024, 100% from 2024/2025 — the min-8 rule absorbs the early gaps; arm inactive where the window cannot fill |
| X8 | Referee yellow rate (trailing) | **ADOPTED** (arm) | F8: r=0.561, coverage 100%. Same operational caveat as J1: no published appointment ⇒ base arm, no imputation |
| X9 | Reference territorial covariates (possession, big chances) | **ADOPTED** (Gate Zero) | F9: possession r=0.906, big-chance r=0.723 in DK |

## Rejected (inherited from J1 §3, re-affirmed on DK data)

- Team half shares (all stats): NOISE (F3) — frozen constants only:
  goals 0.463, SOT 0.462, corners 0.488, shots 0.470, yellows 0.319.
- Trailing finishing (r=0.246, NOISE), trailing conversion, standalone
  on-target rate as a covariate (r=0.310 weak; v5's internal
  Beta-Binomial ratio component is an architectural component, and
  the RS arm tests its shrinkage — the covariate itself stays out).
- Defensive xGOT (never measured as signal anywhere; X6 dropped whole).
- Lineup/absence (CLOSED, F10), standings/h2h snapshots (leakage),
  attendance (not pre-match), red cards as target (rare-event count).
