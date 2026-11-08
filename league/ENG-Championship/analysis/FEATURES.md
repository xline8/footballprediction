# Phase 3.5 — Feature Engineering (J1 template X1–X9, judged on ENG-Championship data)

Consumption rule and causality contract are inherited verbatim from
`league/J1/analysis/FEATURES.md` (trailing/expanding windows only,
strictly pre-match, ratio-of-sums, NaN ⇒ arm inactive, never imputed).
Only the verdicts differ — each was re-measured on this league (EDA).

| # | Feature (J1 analogue) | ENGCH verdict | Evidence |
|---|---|---|---|
| X1 | Blend observation pair (goals + xG) | **ADOPTED** | xG in 100% of matches from 2021/2022; F11 goals/xG 0.994–1.058 per season |
| X2 | Mover tier offset | **ADOPTED** (arm) | F4: both adjacent tiers are in the warehouse (PL id 47, L1 id 108); entry GD +0.490 (from PL) / −0.154 (from L1) per match, n≈600 team-matches per direction. Frozen magnitudes: from-PL ΔGF +0.309 / ΔGA −0.181; from-L1 ΔGF −0.031 / ΔGA +0.122 vs mu 1.265. Applied at prediction time in the entry season only, J1 X2 formulation |
| X3 | Set-play xG share/rate (trailing) | **DROPPED** (not run) | F5 split-half r=0.721 is a clear SIGNAL, but the goals candidate's three arm slots are taken by the two mover/thin-data questions this league's design must answer first (SHRINK, X2) — the template caps variant arms at 2–3 and forbids post-hoc additions. Recorded here so a future prereg can pick X3 up honestly; it is NOT smuggled into this build |
| X4 | xG per shot (trailing) | **ADOPTED** (arm) | F6 r=0.529 |
| X5 | Trailing target-rate means (naive/ensemble) | **ADOPTED** | F2: SOT 0.688, shots 0.712, corners 0.517 — moderate but real. (Yellows −0.010: the naive baseline for cards is a trailing mean of a noise trait; the gate will judge) |
| X6 | Attacking xGOT/shot (era-guarded) | **DROPPED** | F7: era r=0.344 — fails the reliability standard (J1 accepted 0.518), and the population era starts 2024/2025, inside the last dev season, so the arm could never be honestly dev-tested across the dev window (the BR/SCO X6 lesson applied in advance) |
| X7 | Opp-box touches for/against (trailing) | **ADOPTED** (arm) | F2: r=0.841 for. Coverage 78.5–79.2% in 2021/2022–2022/2023, 100% from 2023/2024 — the min-8 rule absorbs the early gaps |
| X8 | Referee yellow rate (trailing) | **DROPPED** | F8: r=0.259 — fails the reliability standard (J1 0.65, DK 0.56). Also referee coverage is 48.3% in the seed season. Not built; K-ENGCH runs Gate Zero only |
| X9 | Reference territorial covariates (possession, big chances) | **ADOPTED** (Gate Zero) | F2: possession r=0.868, big-chance r=0.811 |

## Halves constants (frozen, complete-splits era 2023/2024–2025/2026)

goals 0.4453 · SOT 0.4548 · corners 0.4638 · total shots 0.4573 ·
yellow cards 0.3109. Presentation only, exactly as J1.

## Rejected (inherited from J1 §3, re-affirmed on ENGCH data)

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
  season and by fitted ratings thereafter; a payment flag would be
  a standings-snapshot-style leak risk and is not built.
