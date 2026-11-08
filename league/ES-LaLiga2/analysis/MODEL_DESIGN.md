# Phase 4 — Model Design: ES-LaLiga2 Candidates

Rules inherited from `league/J1/analysis/MODEL_DESIGN.md`: every
candidate names its production reference, Gate Zero is the unmodified
reference fitted per league, variants come only from FEATURES.md
adopted arms (max 2–3 per candidate), gates are the program's frozen
legs, a FAIL is a complete outcome. Feature consumption: FEATURES.md.
Worked analogue: ENG-Championship (2nd tier, play-offs, heavy churn) —
with one structural difference the checkpoint already flagged: the
xG/shotmap era starts inside the virgin here, so the goals candidate
is goals-only and the SOT candidate has no quality-input arm.

Shared frame: dev = walk-forward over 2021/2022–2024/2025 (train seed
2021/2022; evaluation 2022/2023–2024/2025, pooled n=1,404,
season-blocked); virgin = 2025/2026 (n=468, complete — see
DATA_UNDERSTANDING §1 for the frozen choice), read ONCE and only for
arms passing the dev gate; 2026/2027 (partial, n=138) reserved
un-read as the confirmatory window. Baselines: league base rate
(prior-seasons over-rate at the primary line) and naive trailing-10
(count markets) / climatology (goals). Calibration rule: |breach|
≤ 1pp clean PASS; ≤ 1 SE PROVISIONAL PASS; else FAIL. Primary line
per candidate = the .5 line whose dev over-rate is closest to 0.5.
All model state is keyed on FotMob team_id (Phase 2 rule 9).

| Candidate | Reference | Primary line (dev over-rate) | Arms |
|---|---|---|---|
| G-ES goals | production DC (model_v2 pattern), **goals-only** (X1 era-dead — documented fallback, J2 precedent) | OU 2.5 (0.400 pooled dev) + 1X2 LL/RPS | Gate Zero; SHRINK (thin-data prior — sanctioned G-J2-lesson arm); X2 mover tier offset (F4 magnitudes, LaLiga/PrimeraFed) |
| S-ES SOT | model_sot.py v5 | 7.5 (dev 0.491) | Gate Zero; RS ratio-shrink (X4/X6 era-dead — not built) |
| C-ES corners | model_corners_v3 | 9.5 (dev 0.448) | Gate Zero (X9 covariates); X7 box-touch multiplier |
| K-ES cards | model_cards.py | 4.5 (dev 0.536) | Gate Zero only (X8 dropped in FEATURES, dev r=0.180; target = event-feed yellows) |
| T-ES total shots | shots family (v1/v2/E9, as T-J1) | 23.5 (dev 0.481) | A v1 pattern; B v2 level layer; C E9 trailing-r |

Notes:
- G-ES is goals-only **by design**, per the task brief and Phase 1:
  `expected_goals` exists in 7 of 1,872 dev matches and the xG era
  starts inside the virgin — building an xG arm on one era is
  explicitly not done. Gate Zero here is the reference architecture
  with its documented goals-only observation (exactly G-J2's
  construction), so SHRINK and X2 are tested against the true
  reference, not a straw man.
- SHRINK and X2 are both pre-registered here, before any fitting:
  SHRINK per the template's explicit G-J2-lesson sanction, X2 as
  this league's F4-measured feature. With 7 new clubs every season
  (32% churn — the heaviest in the program alongside ENGCH), season
  openers are where an unmodified DC is most exposed — the two arms
  attack that exposure from opposite sides (shrink the thin-data
  rating; inform the mover's prior from its tier step). The ES tier
  steps are defence-led (F4), the mirror image of ENGCH's
  attack-led Premier League step.
- K-ES's target is the event-feed yellow count (Phase 1 §3): the
  stats feed is not one consistent quantity in this league. The
  cards Gate Zero architecture is otherwise the unmodified
  reference, fed the unified target exactly as AR/IN fed theirs.
- S-ES runs only two arms because both quality-input arms are
  era-dead; the arm cap is a ceiling, not a quota.
- Churn strength is a property of the league, not a defect: no arm
  clamps ratings; the virgin calibration leg will judge the fitted
  lambdas as they are. The virgin season also ran hot on every
  count market (EDA F1) — recorded here so the calibration outcomes
  are read against the regime, not re-litigated after the fact.
- Halves presentation (all markets): FT + 1H/2H via the frozen ES
  constants, presentation only, exactly as J1.
- Play-off rounds are ordinary rows in every fit (PREPROCESSING
  rule 3); no phase feature is used anywhere.
- Predictions-only: no ES odds/settlement source in-system.
