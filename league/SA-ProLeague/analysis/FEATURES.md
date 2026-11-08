# Phase 3.5 — Feature Engineering (J1 template X1–X9, judged on SA data)

Consumption rule and causality contract are inherited verbatim from
`league/J1/analysis/FEATURES.md` (trailing/expanding windows only,
strictly pre-match, ratio-of-sums, NaN ⇒ arm inactive, never
imputed). Only the verdicts differ — each was re-measured on this
league (EDA). The era guard is this league's central discipline:
**no xG quantity exists before 2023/2024** (2.5%/13.3% coverage),
and that boundary is also the regime break.

| # | Feature (J1 analogue) | SA verdict | Evidence |
|---|---|---|---|
| X1 | Blend observation pair (goals + xG) | **ADOPTED with era guard** | xG in 100% of matches from 2023/2024, ~absent before; F11 post-break goals/xG 1.032–1.074 (calibrated). Pre-break observations enter goals-only, the reference blend's documented fallback |
| X2 | Mover tier offset | **DROPPED** | No feeder tier in this corpus — the offset is not estimable (as SCO). Replaced in the goals design by the SHRINK thin-data arm (sanctioned G-J2 lesson), an architectural prior, not X2. New/promoted clubs are frequent here (18-team expansion + churn), so the thin-data problem is real |
| X3 | Set-play xG share/rate (trailing) | **ADOPTED** (arm, post-era only) | F5 split-half r=0.514 on 2023/2024+ |
| X4 | xG per shot (trailing) | **ADOPTED** (arm, post-era only) | F6 r=0.654 on 2023/2024+ |
| X5 | Trailing target-rate means (naive/ensemble) | **ADOPTED** | F2 post-era: SOT 0.887, corners 0.910, shots 0.929; yellows WEAK at 0.264 — adopted because it is part of the reference architectures and the naive baseline, with the weakness on the record |
| X6 | Attacking xGOT/shot (era-guarded) | **ADOPTED as feature, NOT RUN as arm** | F7: era r=0.545 (2024/2025+ population era, 99.4%+ shot coverage). The era starts inside the last dev season, so the arm could never be honestly dev-tested across the dev window — recorded here as the SCO/BR X6 lesson applied in advance |
| X7 | Opp-box touches for/against (trailing) | **ADOPTED** (arm) | F2 post-era r=0.953 for. Coverage 62.9%/80.8% pre-break, 100% from 2023/2024 — the min-8 rule absorbs the early gaps |
| X8 | Referee yellow rate (trailing) | **DROPPED** | F8: r=−0.279 (NOISE) on post-era dev seasons; referee coverage 70.9–73.5% in dev, **0.7% in the virgin season** — the arm could not even be computed live. Not built; K-SA runs Gate Zero only |
| X9 | Reference territorial covariates (possession, big chances) | **ADOPTED** (Gate Zero) | F2 post-era: possession r=0.962, big-chance r=0.878 |

## League-specific candidates considered and rejected

- **Climate / altitude covariate** (home-venue highland indicator):
  DROPPED at the descriptive check — highland home edge −0.088
  (n=68) vs lowland +0.193 (EDA F10); the standard reliability
  discipline is not met and the sign is wrong for the hypothesis.
- **Regime-break indicator as a covariate**: not a feature — the
  break is handled structurally (dev scored post-break only;
  pre-break history enters fits decayed), never as a per-match
  dummy the model could lean on in the virgin season.

## Halves constants (frozen, complete-splits era 2023/2024–2025/2026)

goals 0.4251 · SOT 0.4469 · corners 0.4740 · total shots 0.4559 ·
yellow cards 0.3509 (event-based). Presentation only, exactly as J1.

## Rejected (inherited from J1 §3, re-affirmed on SA data)

- Team half shares (all stats): NOISE (F3) — frozen constants only.
- Standalone trailing on-target rate / finishing as covariates
  (v5's internal Beta-Binomial ratio is an architectural component;
  the RS arm tests its shrinkage — the covariate itself stays out).
- Lineup/absence (CLOSED per program history), standings/h2h
  snapshots (leakage), red cards as target (rare-event count).
