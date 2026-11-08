# Phase 3.5 — Feature Engineering (J1 template X1–X9, judged on SCO data)

Consumption rule and causality contract are inherited verbatim from
`league/J1/analysis/FEATURES.md` (trailing/expanding windows only,
strictly pre-match, ratio-of-sums, NaN ⇒ arm inactive, never imputed).
Only the verdicts differ — each was re-measured on this league (EDA).

| # | Feature (J1 analogue) | SCO verdict | Evidence |
|---|---|---|---|
| X1 | Blend observation pair (goals + xG) | **ADOPTED** | xG in 100% of matches from 2021/2022; F11 goals/xG 0.989–1.106 per season |
| X2 | Mover tier offset | **DROPPED** | No feeder tier in corpus — the offset is not estimable. Replaced in the goals design by the SHRINK thin-data arm (sanctioned G-J2 lesson), an architectural prior, not X2 |
| X3 | Set-play xG share/rate (trailing) | **ADOPTED** (arm) | F5 split-half r=0.676 |
| X4 | xG per shot (trailing) | **ADOPTED** (arm) | F6 r=0.740 |
| X5 | Trailing target-rate means (naive/ensemble) | **ADOPTED** | F2: SOT 0.972, corners 0.963, shots 0.969, yellows 0.639 |
| X6 | Attacking xGOT/shot (era-guarded) | **ADOPTED** (arm, era guard 2024/2025+) | F7: era r=0.490, near J1's accepted 0.518; population era starts 2024/2025 (94%+ coverage). Arm status only — the dev gate decides, and the arm is inactive before the era by construction |
| X7 | Opp-box touches for/against (trailing) | **ADOPTED** (arm) | F2/F9: r=0.966 for. Coverage 73.7–88.6% in 2021/2022–2023/2024, 100% from 2024/2025 — the min-8 rule absorbs the early gaps |
| X8 | Referee yellow rate (trailing) | **DROPPED** | F8: r=0.158 — fails the reliability standard outright (J1 0.65, DK 0.56). Not built; K-SCO runs Gate Zero only |
| X9 | Reference territorial covariates (possession, big chances) | **ADOPTED** (Gate Zero) | F2: possession r=0.985, big-chance r=0.953 |

## Halves constants (frozen, complete-splits era 2023/2024–2025/2026)

goals 0.4405 · SOT 0.4492 · corners 0.4704 · total shots 0.4582 ·
yellow cards 0.3120. Presentation only, exactly as J1.

## Rejected (inherited from J1 §3, re-affirmed on SCO data)

- Team half shares (all stats): NOISE (F3) — frozen constants only.
- Standalone trailing on-target rate / finishing as covariates
  (v5's internal Beta-Binomial ratio is an architectural component;
  the RS arm tests its shrinkage — the covariate itself stays out).
- Lineup/absence (CLOSED per program history), standings/h2h
  snapshots (leakage), red cards as target (rare-event count).
- Phase (regular/split) as a feature: split rounds are ordinary
  rows; no phase covariate anywhere.
