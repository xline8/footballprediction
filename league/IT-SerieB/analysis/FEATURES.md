# Step 5 — Features: IT-SerieB (X1–X9, J1 template judged in-league)

Consumption rule and causality contract are inherited verbatim from
`league/J1/analysis/FEATURES.md` (trailing/expanding windows only,
strictly pre-match, ratio-of-sums, NaN ⇒ arm inactive, never
imputed). Team identity is keyed on FotMob team_id throughout
(Phase 2 rule 9, with the documented Reggiana alias); the only
name-keyed test (X2 membership) uses accent-normalised names plus
the `ac reggiana 1919` → `reggiana` spelling alias, verified 1:1
against ids.

| # | Feature (J1 analogue) | ITB verdict | Evidence |
|---|---|---|---|
| X1 | Blend observation pair (goals + xG) | **DROPPED** (era-dead) | `expected_goals` exists in 13 of 1,559 dev matches (4/390, 5/390, 1/390, 3/389 per dev season); the xG era starts in the virgin 2025/2026. A blend arm could never be dev-tested. The goals fit is therefore **goals-only** — the production reference's own documented fallback (J2/ES precedent), not a modified Gate Zero |
| X2 | Mover tier offset | **ADOPTED** (arm) | F4: both adjacent tiers are in the warehouse (Serie A id 55, Serie C id 147); exactly 3 + 4 movers every season (35% churn). Entry GD +0.288 (from Serie A) / −0.188 (from Serie C) per match. Frozen magnitudes vs mu 1.232: from-Serie A ΔGF +0.145 / ΔGA −0.143; from-Serie C ΔGF −0.070 / ΔGA +0.118. Applied at prediction time in the entry season only, ENGCH/ES X2 formulation; membership by frozen per-season mover table derived from team_id churn + tier name matching (engine carries the table, see PREREG_G_ITB) |
| X3 | Set-play xG share/rate (trailing) | **DROPPED** (era-dead) | F5: set-play xG splits absent from the dev window (same 13 matches as X1). Not measurable, not built |
| X4 | xG per shot (trailing) | **DROPPED** (era-dead) | F6: shotmap exists in 12 of 1,559 dev matches; the era starts in the virgin. S-ITB therefore runs Gate Zero + RS only |
| X5 | Trailing target-rate means (naive/ensemble) | **ADOPTED** | F2: SOT-for 0.555, shots-for 0.367, corners-for 0.296 (weak-moderate), yellows-for (events) 0.475 — real traits, churn-diluted like ES |
| X6 | Attacking xGOT/shot (era-guarded) | **DROPPED** (era-dead) | F7: xGOT is populated only from 2025/2026 — the era *is* the virgin, so no era guard can create a dev window |
| X7 | Opp-box touches for / against (trailing) | **DROPPED** (reliability) | F2: box touches-for r=0.320 on only 16 qualifying teams, box touches-against r=−0.129 (noise) — far below the adoption standard (J1/ES 0.66–0.71 both sides). Coverage is also 74.4–76.9% in 2021/2022–2022/2023. Not built; C-ITB runs Gate Zero (X9) only |
| X8 | Referee yellow rate (trailing) | **DROPPED** | F8: r=0.061 on dev seasons — the weakest referee signal in the program (J1 0.65, DK 0.56; ES dropped at 0.180). Referee coverage is also 47.4% in the seed season. Not built; K-ITB runs Gate Zero only |
| X9 | Reference territorial covariates (possession, big chances) | **ADOPTED** (Gate Zero) | F2: possession r=0.788, big-chance-for r=0.352; both keys in 100% of matches in every season |
| SHRINK | Thin-data rating shrinkage | **ADOPTED as a pre-registered arm** | Template-sanctioned G-J2-lesson arm: for teams with fewer than six prior in-league matches, scale ratings by n/6. With 35% churn, season openers are exactly the exposure |

## Halves constants (frozen, complete seasons 2023/2024–2025/2026)

goals 0.4501 · SOT 0.4598 · corners 0.4734 · total shots 0.4650 ·
yellows (events) 0.3733. Presentation only, exactly as J1.

## Rejected (inherited from J1 §3, re-affirmed on ITB data)

- Team half shares (all stats): NOISE (F3) — frozen constants only.
- Standalone trailing on-target rate / finishing as covariates
  (v5's internal Beta-Binomial ratio is an architectural component;
  the RS arm tests its shrinkage — the covariate itself stays out).
- Lineup/absence (CLOSED per program history), standings/h2h
  snapshots (leakage), red cards as target (rare-event count).
- Phase (regular/play-off/play-out) as a feature: play-off rows are
  ordinary rows; no phase covariate anywhere.
- Any xG/shotmap-derived covariate for a *future* arm: eligible only
  once a full dev window exists inside the xG era (earliest honest
  test: a prereg written after 2026/2027 completes). Recorded so the
  era-dead drops are not mistaken for permanent rejections.
