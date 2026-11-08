# Phase 3.5 — Feature Engineering (J1 template X1–X9, judged on IN data)

Consumption rule and causality contract are inherited verbatim
from `league/J1/analysis/FEATURES.md` (trailing/expanding windows
only, strictly pre-match, ratio-of-sums, NaN ⇒ arm inactive,
never imputed). Only the verdicts differ — each was re-measured
on this league (EDA).

| # | Feature (J1 analogue) | IN verdict | Evidence |
|---|---|---|---|
| X1 | Blend observation pair (goals + xG) | **ADOPTED** (with caveat) | xG in 100% of matches from 2021/2022; F11: goals/xG ≈ 1.19 pooled — a systematic scale gap recorded against G-IN; the unmodified production pattern remains Gate Zero |
| X2 | Mover tier offset | **DROPPED** | No relegation and no feeder tier in corpus (F4) — the offset does not exist. Replaced in the goals design by the SHRINK thin-data arm (sanctioned G-J2 lesson), an architectural prior, not X2 |
| X3 | Set-play xG share/rate (trailing) | **ADOPTED** (arm) | F5 split-half r=0.489 |
| X4 | xG per shot (trailing) | **ADOPTED** (arm) | F6 r=0.514 |
| X5 | Trailing target-rate means (naive/ensemble) | **ADOPTED** | F2: SOT 0.820, shots 0.794, corners 0.681, yellows (events) moderate — team yellows-for 0.469 measured on the stats column; the event target is the same construct from the fuller feed |
| X6 | Attacking xGOT/shot (era-guarded) | **DROPPED** | F7: era begins 2024/2025 (one dev season), era trait weak r≈0.35 — the arm would be dev-untestable; not built |
| X7 | Opp-box touches for/against (trailing) | **ADOPTED** (arm) | F9: r=0.783 for / 0.850 against; coverage 100% all seasons |
| X8 | Referee yellow rate (trailing) | **DROPPED** | F8: coverage 13.5% in dev, **0% in the virgin**; most frequent referee has 11 matches — no trait is even computable. Not built — K-IN is Gate-Zero-only |
| X9 | Reference territorial covariates (possession, big chances) | **ADOPTED** (Gate Zero) | F9: possession r=0.910, big-chance r=0.502 in IN |

## Rejected (inherited from J1 §3, re-affirmed on IN data)

- Team half shares (all stats): NOISE (F3) — frozen constants
  only: goals 0.435, SOT 0.453, corners 0.458, shots 0.447,
  yellows 0.366.
- Standalone on-target rate as a covariate: measured r=0.452 in
  IN (not noise here — F6), but the template rejection stands:
  v5's internal Beta-Binomial ratio component is an architectural
  component, and the RS arm tests its shrinkage — the covariate
  itself stays out.
- Trailing finishing: measured r=0.464 in IN (F6) — recorded as
  a league difference from J1, **not consumed** by any template
  arm in this prereg; a future prereg may revisit it with its
  own design.
- Defensive xGOT (never measured as signal anywhere; X6 is
  attacking-only and is dropped here regardless).
- Lineup/absence (CLOSED, F10), standings/h2h snapshots
  (leakage), attendance (not pre-match), red cards as target
  (rare-event count).
