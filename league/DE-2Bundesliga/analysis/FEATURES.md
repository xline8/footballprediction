# Phase 3.5 — Feature Engineering (J1 template X1–X9, judged on DE-2 data)

Consumption rule and causality contract are inherited verbatim from
`league/J1/analysis/FEATURES.md` (trailing/expanding windows only,
strictly pre-match, ratio-of-sums, NaN ⇒ arm inactive, never
imputed). Only the verdicts differ — each was re-measured on this
league (EDA).

| # | Feature (J1 analogue) | DE-2 verdict | Evidence |
|---|---|---|---|
| X1 | Blend observation pair (goals + xG) | **ADOPTED** | xG in 1,629/1,629 matches from 2021/2022 (no fallbacks needed); F12 goals/xG ≈ 1.03 pooled, 1.02–1.06 per dev season |
| X2 | Mover tier offset | **ADOPTED** (arm, direction-specific) | F5: BOTH feeder tiers are in the warehouse; entrants 4–5/season. Dev-pooled first-season deltas: up (from 3. Liga) ΔGF −0.360 / ΔGA +0.143 (9 clubs); down (from Bundesliga) ΔGF +0.097 / ΔGA +0.078 (6 clubs). The offset is estimated inside each fit from transitions completed before the target season (estimation rule frozen in PREREG_G_DE2); this table is the plausibility check, not constants. Direction from neighbour membership (`analysis/movers.py`) |
| X3 | Set-play xG share/rate (trailing) | **ADOPTED** (arm) | F6 split-half r=0.558 — strong; arm status only, gate decides |
| X4 | xG per shot (trailing) | **ADOPTED** (arm) | F7 r=0.529 — the strongest xG/shot reading in the program (BE adopted at 0.435). S-DE2 runs Gate Zero + RS + X4 |
| X5 | Trailing target-rate means (naive/ensemble) | **ADOPTED** | F2: shots 0.788, SOT 0.739, corners 0.644, yellows 0.558 reliable — the naive baseline is defined identically, the gate decides |
| X6 | Attacking xGOT/shot (era-guarded) | **DROPPED** | F8: era-guarded (2024/2025+) split-half r=0.182 — noise (DK dropped at 0.212). Not built |
| X7 | Opp-box touches for/against (trailing) | **ADOPTED** (arm) | F10: r=0.842 for / 0.619 against. Coverage 61–80% in 2021/2022–2023/2024, 100% from 2024/2025 — the min-8 rule absorbs the early gaps; arm inactive where the window cannot fill |
| X8 | Referee yellow rate (trailing) | **ADOPTED** (arm) | F9: r=0.470, 38 referees ≥20 matches. Coverage 46.4% in 2021/2022 → 88–100% from 2022/2023; early dev values are often the shrunk league mean. Same operational caveat as J1: no published appointment ⇒ base arm, no imputation |
| X9 | Reference territorial covariates (possession, big chances) | **ADOPTED** (Gate Zero) | F10: possession r=0.906, big-chance r=0.772 in DE-2 |

## Rejected (inherited from J1 §3, re-affirmed on DE-2 data)

- Team half shares (all stats): NOISE (F3) — frozen constants only:
  goals 0.450, SOT 0.443, corners 0.454, shots 0.447, yellows 0.346.
- Trailing finishing, trailing conversion, standalone on-target rate
  as a covariate (r=0.299 — weak in DE-2, F7, and rejected per the
  J1 template in any case: v5's internal Beta-Binomial ratio
  component is an architectural component, and the RS arm tests its
  shrinkage — the covariate itself stays out).
- Defensive xGOT (never measured as signal anywhere; X6 dropped whole).
- Lineup/absence (CLOSED, F11), standings/h2h snapshots (leakage),
  attendance (not pre-match), red cards as target (rare-event count).
- Any phase feature: there is no phase structure in this corpus
  (DATA_UNDERSTANDING §1); the `qualification` guard flag is a
  preprocessing record, never a model input.
