# Phase 3.5 — Feature Engineering (J1 template X1–X9, judged on ENG-LeagueOne data)

Consumption rule and causality contract are inherited verbatim from
`league/J1/analysis/FEATURES.md` (trailing/expanding windows only,
strictly pre-match, ratio-of-sums, NaN ⇒ arm inactive, never imputed).
Only the verdicts differ — each was re-measured on this league (EDA).

| # | Feature (J1 analogue) | ENGL1 verdict | Evidence |
|---|---|---|---|
| X1 | Blend observation pair (goals + xG) | **ADOPTED** | xG in 100% of matches from 2022/2023; seed season 2021/2022 goals-only fallback (3.2% xG) — the TR era rule. F11 goals/xG 1.155→1.011 across the era |
| X2 | Mover tier offset | **ADOPTED** (arm) | F4: tier above in warehouse (Championship id 48); tier below NOT in warehouse — promoted clubs identified exactly as new clubs not in the Championship list. Entry GD +0.393 (from Championship) / −0.246 (from League Two), n=596/792 team-matches. Frozen magnitudes: from-Ch ΔGF +0.240 / ΔGA −0.153; from-L2 ΔGF −0.127 / ΔGA +0.119 vs mu 1.304. Applied at prediction time in the entry season only, J1 X2 formulation |
| X3 | Set-play xG share/rate (trailing) | **DROPPED** (not run) | F5 split-half r=0.456 — a real but moderate trait, below the signals the program has acted on (J1 0.62, ENGCH 0.721); AND the xG era starts in 2022/2023, the first dev evaluation season, so a trailing set-play arm would be inactive under its min-8 rule for much of dev and could not be honestly dev-tested across the window (the ES/BR era lesson). Recorded here so a future prereg can pick X3 up honestly; it is NOT smuggled into this build |
| X4 | xG per shot (trailing) | **ADOPTED** (arm) | F6 r=0.457; shotmap coverage 100% in every dev evaluation season (era-clean for this use; early-2022/2023 fallback to Gate Zero under min-8, as pre-registered) |
| X5 | Trailing target-rate means (naive/ensemble) | **ADOPTED** | F2: SOT 0.799, shots 0.886, corners 0.615 — real. (Yellows 0.309: weak; the naive cards baseline is a trailing mean of a thin trait; the gate will judge) |
| X6 | Attacking xGOT/shot (era-guarded) | **DROPPED** | F7: era r=−0.094 — pure noise; population era also starts 2024/2025, inside the last dev season |
| X7 | Opp-box touches for/against (trailing) | **ADOPTED** (arm) | F2: r=0.870 for. Coverage 75.9–79.2% in 2021/2022–2022/2023, 85.6% in 2023/2024, 100% from 2024/2025 — the min-8 rule absorbs the early gaps |
| X8 | Referee yellow rate (trailing) | **DROPPED** | F8: r=0.305 — fails the reliability standard (J1 0.65, DK 0.56). Coverage is fine (~100% after the seed season); the trait does not persist. Not built; K-ENGL1 runs Gate Zero only |
| X9 | Reference territorial covariates (possession, big chances) | **ADOPTED** (Gate Zero) | F2: possession r=0.962, big-chance r=0.791 |

## Halves constants (frozen, complete-splits era)

goals 0.4425 · SOT 0.4414 · corners 0.4672 · total shots 0.4551 ·
yellow cards 0.3277. Presentation only, exactly as J1.

## Rejected (inherited from J1 §3, re-affirmed on ENGL1 data)

- Team half shares (all stats): NOISE (F3) — frozen constants only.
- Standalone trailing on-target rate / finishing as covariates
  (v5's internal Beta-Binomial ratio is an architectural component;
  the RS arm tests its shrinkage — the covariate itself stays out).
- Lineup/absence (CLOSED per program history), standings/h2h
  snapshots (leakage), red cards as target (rare-event count).
- Phase (regular/play-off) as a feature: play-off rounds are
  ordinary rows; no phase covariate anywhere.
- Parachute-payment indicators as a separate covariate: the effect
  is already carried by the X2 entry offset in a mover's first
  season and by fitted ratings thereafter; not built (as ENGCH).
