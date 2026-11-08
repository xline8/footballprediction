# Phase 3.5 — Feature Engineering (J1 template X1–X9, judged on ES-LaLiga2 data)

Consumption rule and causality contract are inherited verbatim from
`league/J1/analysis/FEATURES.md` (trailing/expanding windows only,
strictly pre-match, ratio-of-sums, NaN ⇒ arm inactive, never imputed).
Only the verdicts differ — each was re-measured on this league (EDA),
or dropped on availability where the data does not exist in the dev
window. Team identity is keyed on FotMob team_id throughout (Phase 2
rule 9); the only name-keyed test (X2 membership) uses
accent-normalised names, verified 1:1 against ids.

| # | Feature (J1 analogue) | ES verdict | Evidence |
|---|---|---|---|
| X1 | Blend observation pair (goals + xG) | **DROPPED** (era-dead) | `expected_goals` exists in 7 of 1,872 dev matches (1/468, 3/468, 0/468, 3/468 per dev season); the xG era starts in the virgin 2025/2026. A blend arm could never be dev-tested. The goals fit is therefore **goals-only** — the production reference's own documented fallback (J2 precedent), not a modified Gate Zero |
| X2 | Mover tier offset | **ADOPTED** (arm) | F4: both adjacent tiers are in the warehouse (LaLiga id 87, Primera Federación id 8968); exactly 3 + 4 movers every season. Entry GD +0.251 (from LaLiga) / −0.136 (from PrimeraFed) per match. Frozen magnitudes vs mu 1.191: from-LaLiga ΔGF +0.080 / ΔGA −0.171; from-PrimeraFed ΔGF −0.025 / ΔGA +0.111. Applied at prediction time in the entry season only, ENGCH X2 formulation; membership by accent-normalised team name in the warehouse index |
| X3 | Set-play xG share/rate (trailing) | **DROPPED** (era-dead) | F5: set-play xG splits absent from the dev window (same 7 matches as X1). Not measurable, not built |
| X4 | xG per shot (trailing) | **DROPPED** (era-dead) | F6: shotmap exists in 7 of 1,872 dev matches; the shotmap era starts in the virgin. S-ES therefore runs Gate Zero + RS only |
| X5 | Trailing target-rate means (naive/ensemble) | **ADOPTED** | F2: SOT-for 0.641, shots-for 0.628, corners-for 0.553, yellows-for (events) 0.453 — moderate but real, churn-diluted like ENGCH |
| X6 | Attacking xGOT/shot (era-guarded) | **DROPPED** (era-dead) | F7: xGOT is populated only from 2025/2026 — the era *is* the virgin, so no era guard can create a dev window |
| X7 | Opp-box touches for / against (trailing) | **ADOPTED** (arm) | F2: r=0.707 for, 0.659 against. Coverage 75.0–87.2% in 2021/2022–2023/2024, 100% from 2024/2025 — the min-8 rule absorbs the early gaps (ENGCH pattern) |
| X8 | Referee yellow rate (trailing) | **DROPPED** | F8: r=0.180 on dev seasons (0.269 pooled) — fails the reliability standard (J1 0.65, DK 0.56). Referee coverage is also 48.5% in the seed season and 82.1% in the virgin. Not built; K-ES runs Gate Zero only |
| X9 | Reference territorial covariates (possession, big chances) | **ADOPTED** (Gate Zero) | F2: possession r=0.899, big-chance-for r=0.761; both keys in 100% of matches in every season |

## Halves constants (frozen, complete-splits era 2023/2024–2025/2026)

goals 0.4322 · SOT 0.4491 · corners 0.4692 · total shots 0.4522 ·
yellows (events) 0.3455. Presentation only, exactly as J1.

## Rejected (inherited from J1 §3, re-affirmed on ES data)

- Team half shares (all stats): NOISE (F3) — frozen constants only.
- Standalone trailing on-target rate / finishing as covariates
  (v5's internal Beta-Binomial ratio is an architectural component;
  the RS arm tests its shrinkage — the covariate itself stays out).
- Lineup/absence (CLOSED per program history), standings/h2h
  snapshots (leakage), red cards as target (rare-event count).
- Phase (regular/play-off) as a feature: play-off rounds are
  ordinary rows; no phase covariate anywhere.
- Any xG/shotmap-derived covariate for a *future* arm: eligible only
  once a full dev window exists inside the xG era (earliest honest
  test: a prereg written after 2026/2027 completes, dev on
  2025/2026–2026/2027). Recorded so the era-dead drops are not
  mistaken for permanent rejections of the features themselves.
