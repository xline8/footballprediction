# Phase 3.5 — Feature Engineering (J1 template X1–X9, judged on BR data)

Consumption rule and causality contract are inherited verbatim from
`league/J1/analysis/FEATURES.md` (trailing/expanding windows only,
strictly pre-match, ratio-of-sums, NaN ⇒ arm inactive, never
imputed). Only the verdicts differ — each was re-measured on this
league (EDA).

| # | Feature (J1 analogue) | BR verdict | Evidence |
|---|---|---|---|
| X1 | Blend observation pair (goals + xG) | **ADOPTED** | F11: xG calibrated 2023+ (0.984–1.007); coverage 99.7–100% from 2023, ~7–10% in 2021/2022 → blend falls back to goals-only there (production behaviour), sparse subset never used as evidence |
| X2 | Mover tier offset | **ADOPTED** (arm) | F4: Série B (id 8814) is in the warehouse; promoted sides' GA jumps +0.45…+0.59 vs own B level, GF −0.2…−0.3; offset estimated inside the dev fit from pre-season transitions only (J1 leakage guard) |
| X3 | Set-play xG share/rate (trailing) | **ADOPTED** (arm) | F5 split-half r=0.473; xG-era only, min-8 rule → arm inactive until windows fill (effectively 2023+ dev) |
| X4 | xG per shot (trailing) | **ADOPTED** (arm) | F6 r=0.571 — strongest X4 reading in the program; shotmap era 2023+, min-8 else Gate Zero fallback |
| X5 | Trailing target-rate means (naive/ensemble) | **ADOPTED** | F2: SOT 0.749, corners 0.597, yellows 0.708, shots 0.697 |
| X6 | Attacking xGOT/shot (era-guarded) | **DROPPED** | F7: era begins 2025 = the virgin season itself (r=0.348 there) — the arm could never be exercised in dev; unguarded r=0.816 is a population artefact. Not built |
| X7 | Opp-box touches for/against (trailing) | **ADOPTED** (arm) | F9: r=0.803 for / 0.789 against. Coverage ~45% in 2021–2023, 100% from 2024 — min-8 rule absorbs the gaps |
| X8 | Referee yellow rate (trailing) | **ADOPTED** (arm) | F8: r=0.353 (weak; DK X4 precedent — gate decides), coverage 0% in 2021 then 90–98%; virgin 2025 coverage 90%. No published appointment ⇒ base arm, no imputation |
| X9 | Reference territorial covariates (possession, big chances) | **ADOPTED** (Gate Zero) | F9: possession r=0.928, big-chance r=0.785 in BR |

Plus, for G-BR only, the **SHRINK thin-data prior** (the sanctioned
G-J2-lesson arm, pre-registered in MODEL_DESIGN): ratings of teams
with <6 in-league matches shrunk toward the league mean. With 4
promoted sides arriving every season, BR has the program's largest
thin-data exposure; SHRINK and X2 are distinct responses (prior
shrinkage for any thin team vs an estimated tier-step for movers)
and are registered as separate arms, never stacked unless the
prereg says so.

## Rejected (inherited from J1 §3, re-affirmed on BR data)

- Team half shares (all stats): NOISE (F3) — frozen constants only:
  goals 0.455, SOT 0.462, corners 0.474, shots 0.463, yellows 0.366.
- Trailing finishing (r=0.110, NOISE), trailing conversion,
  standalone on-target rate as a covariate (r=0.264 weak; v5's
  internal Beta-Binomial ratio component is an architectural
  component, and the RS arm tests its shrinkage — the covariate
  itself stays out).
- Defensive xGOT and the X6 arm whole (F7).
- Lineup/absence (CLOSED, F10), standings/h2h snapshots (leakage),
  attendance (not pre-match), red cards as target (rare-event
  count; reds are 0.25/match here — higher than J1 but still a
  rare-event count with no reliability evidence).
