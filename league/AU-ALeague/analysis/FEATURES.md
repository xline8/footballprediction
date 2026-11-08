# Phase 3.5 — Feature Engineering (J1 template X1–X9, judged on AU data)

Consumption rule and causality contract are inherited verbatim
from `league/J1/analysis/FEATURES.md` (trailing/expanding windows
only, strictly pre-match, ratio-of-sums, NaN ⇒ arm inactive,
never imputed). Only the verdicts differ — each was re-measured
on this league (EDA).

| # | Feature (J1 analogue) | AU verdict | Evidence |
|---|---|---|---|
| X1 | Blend observation pair (goals + xG) | **ADOPTED** | xG in 100% of matches from 2021/2022; F11 calibration 1.002 pooled |
| X2 | Mover tier offset | **DROPPED** | No relegation and no feeder tier in corpus (F4) — the offset does not exist. Replaced in the goals design by the SHRINK thin-data arm (sanctioned G-J2 lesson), an architectural prior, not X2 |
| X3 | Set-play xG share/rate (trailing) | **ADOPTED** (arm) | F5 split-half r=0.724 — strongest in the program |
| X4 | xG per shot (trailing) | **ADOPTED** (arm) | F6 r=0.576 — strongest of J1/DK/AU |
| X5 | Trailing target-rate means (naive/ensemble) | **ADOPTED** | F2: shots 0.824, SOT 0.678, corners 0.716, yellows 0.351 (weak — recorded against K-AU) |
| X6 | Attacking xGOT/shot (era-guarded) | **ADOPTED** (arm) | F7: era-guarded (2024/2025+) split-half r=0.543, replicating J1 (0.518), not DK (0.212) |
| X7 | Opp-box touches for/against (trailing) | **ADOPTED** (arm) | F9: r=0.843 for / 0.882 against. Coverage 90–97% in 2021/2022–2022/2023, 100% from 2023/2024 — the min-8 rule absorbs the early gaps; arm inactive where the window cannot fill |
| X8 | Referee yellow rate (trailing) | **DROPPED** | F8: r=0.06 (noise) AND coverage only 76.7–97.0% (82.8% in the virgin season). Both legs of the adoption test fail. Not built — K-AU is Gate-Zero-only |
| X9 | Reference territorial covariates (possession, big chances) | **ADOPTED** (Gate Zero) | F9: possession r=0.890, big-chance r=0.502 in AU |

## Rejected (inherited from J1 §3, re-affirmed on AU data)

- Team half shares (all stats): NOISE (F3) — frozen constants
  only: goals 0.432, SOT 0.456, corners 0.452, shots 0.451,
  yellows 0.308.
- Trailing finishing (r=−0.175, NOISE), trailing conversion,
  standalone on-target rate as a covariate (r=0.321 weak; v5's
  internal Beta-Binomial ratio component is an architectural
  component, and the RS arm tests its shrinkage — the covariate
  itself stays out).
- Defensive xGOT (never measured as signal anywhere; X6 is
  attacking-only).
- Lineup/absence (CLOSED, F10), standings/h2h snapshots
  (leakage), attendance (not pre-match), red cards as target
  (rare-event count).
