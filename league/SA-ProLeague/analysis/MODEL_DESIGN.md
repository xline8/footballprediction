# Phase 4 — Model Design: SA-ProLeague Candidates

Rules inherited from `league/J1/analysis/MODEL_DESIGN.md`: every
candidate names its production reference, Gate Zero is the
unmodified reference fitted per league, variants come only from
FEATURES.md adopted arms (max 2–3 per candidate), gates are the
program's frozen legs, a FAIL is a complete outcome. Feature
consumption: FEATURES.md.

## Shared frame — built around the regime break

- **Virgin = 2025/2026 (n=306, complete)**, read ONCE and only for
  arms passing the dev gate. The brief offered 2025/2026
  (transitional) vs 2024/2025 (complete); the warehouse settles it:
  2025/2026 is complete (306 played, ending 2026-05-21), so it is
  the virgin, and **2026/2027 (partial, n=104) is the reserved
  confirmatory window, NOT read** in this build. Freezing the
  most recent *complete* season also matters more than usual here:
  it is the third post-break season, the first virgin in the
  program whose entire recent history is post-break football.
- **Dev = walk-forward scored on the two post-break seasons
  2023/2024 + 2024/2025 (pooled n=612)**; training seed / warm-up
  = 2021/2022–2022/2023 (pre-break). Rationale, stated before any
  fitting: a dev fold scored on pre-break football would reward
  fitting a league that no longer exists (levels +0.28 goals,
  widened spread, shrunken home edge — EDA F1b). Pre-break matches
  still enter fits as decayed history (the references' own decay
  does the down-weighting; no extra break dummy anywhere), and
  the 2023/2024 fold — whose season-blocked goals fit is trained
  almost entirely pre-break — is expected to be the hardest fold.
  It stays in the pooled dev: hiding it would flatter the design.
- Baselines: league base rate (prior-seasons over-rate at the
  primary line) and naive trailing-10 (count markets) /
  climatology (goals). For count markets the base-rate baseline
  for target season 2023/2024 is computed from pre-break history —
  it inherits the break too, which is honest: it is the baseline
  a break-blind model would have used.
- Calibration rule: |breach| ≤ 1pp clean PASS; ≤ 1 SE
  PROVISIONAL PASS; else FAIL.
- Primary line per candidate = the .5 line whose **dev**
  (2023/2024–2024/2025 pooled) over-rate is closest to 0.5.

| Candidate | Reference | Primary line (dev over-rate) | Arms |
|---|---|---|---|
| G-SA goals | production DC + xG blend (model_v2/model_xg pattern) | OU 2.5 (0.565 pooled dev) + 1X2 LL/RPS | Gate Zero; SHRINK (thin-data prior — sanctioned G-J2-lesson arm); X3 set-play decomposition (builds on SHRINK, post-era xG) |
| S-SA SOT | model_sot.py v5 | 8.5 (dev 0.546) | Gate Zero; RS ratio-shrink; X4 xG/shot quality input (post-era shotmap; inactive pre-break by the min-8 rule). X6 adopted as a feature but NOT run (era starts inside the last dev season) |
| C-SA corners | model_corners_v3 | 9.5 (dev 0.510) | Gate Zero (X9 covariates); X7 box-touch multiplier |
| K-SA cards | model_cards.py | 3.5 (dev 0.606) | Gate Zero only (X8 dropped in FEATURES: r=−0.279 and virgin referee coverage 0.7%). Target = unified event yellows |
| T-SA total shots | shots family (v1/v2/E9, as T-J1) | 24.5 (dev 0.503) | A v1 pattern; B v2 level layer; C E9 trailing-r |

Notes:
- G-SA's blend is goals-only for every pre-2023/2024 observation
  (xG feed era, FEATURES X1) — the 2023/2024 dev fold's fit is
  therefore a pure goals fit on pre-break data, and the 2024/2025
  fold's fit is the first that can use xG at all. This is the
  design working as intended, not a defect to patch.
- SHRINK is pre-registered here, before any fitting, per the
  template's explicit sanction; with 18-team expansion plus
  promotion churn, thin-data newcomers are a structural feature
  of this league. No other rescue arms exist.
- Post-break dominance is a property of the league, not a defect:
  no arm clamps ratings; the DC fit is allowed its extreme
  lambdas (Al Hilal +1.863 GD/match), and the virgin calibration
  leg will judge them as they are.
- Halves presentation (all markets): FT + 1H/2H via the frozen SA
  constants, presentation only, exactly as J1.
- Predictions-only: no SA odds/settlement source in-system.
