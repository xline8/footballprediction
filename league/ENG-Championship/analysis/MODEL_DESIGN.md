# Phase 4 — Model Design: ENG-Championship Candidates

Rules inherited from `league/J1/analysis/MODEL_DESIGN.md`: every
candidate names its production reference, Gate Zero is the unmodified
reference fitted per league, variants come only from FEATURES.md
adopted arms (max 2–3 per candidate), gates are the program's frozen
legs, a FAIL is a complete outcome. Feature consumption: FEATURES.md.

Shared frame: dev = walk-forward over 2021/2022–2024/2025 (train seed
2021/2022; evaluation 2022/2023–2024/2025, pooled n=1,671,
season-blocked); virgin = 2025/2026 (n=555, complete — see
DATA_UNDERSTANDING §1 for the frozen choice and the 2 missing
play-off rows), read ONCE and only for arms passing the dev gate;
2026/2027 (partial, n=180) reserved un-read as the confirmatory
window. Baselines: league base rate (prior-seasons over-rate at the
primary line) and naive trailing-10 (count markets) / climatology
(goals). Calibration rule: |breach| ≤ 1pp clean PASS; ≤ 1 SE
PROVISIONAL PASS; else FAIL. Primary line per candidate = the .5
line whose dev over-rate is closest to 0.5.

| Candidate | Reference | Primary line (dev over-rate) | Arms |
|---|---|---|---|
| G-ENGCH goals | production DC + xG blend (model_v2/model_xg pattern) | OU 2.5 (0.475 pooled complete) + 1X2 LL/RPS | Gate Zero; SHRINK (thin-data prior — sanctioned G-J2-lesson arm); X2 mover tier offset (F4 magnitudes, PL/L1) |
| S-ENGCH SOT | model_sot.py v5 | 7.5 (dev 0.512) | Gate Zero; RS ratio-shrink; X4 xG/shot quality input |
| C-ENGCH corners | model_corners_v3 | 9.5 (dev 0.555) | Gate Zero (X9 covariates); X7 box-touch multiplier |
| K-ENGCH cards | model_cards.py | 3.5 (dev 0.560) | Gate Zero only (X8 dropped in FEATURES, r=0.259; team yellows trait itself is noise, r=−0.01) |
| T-ENGCH total shots | shots family (v1/v2/E9, as T-J1) | 23.5 (dev 0.515) | A v1 pattern; B v2 level layer; C E9 trailing-r |

Notes:
- G-ENGCH has xG for every season — the blend never falls back to
  goals-only (contrast J1 2021).
- SHRINK and X2 are both pre-registered here, before any fitting:
  SHRINK per the template's explicit G-J2-lesson sanction, X2 as
  this league's F4-measured feature. With 6 new clubs every season,
  season openers are where an unmodified DC is most exposed — the
  two arms attack that exposure from opposite sides (shrink the
  thin-data rating; inform the mover's prior from its tier step).
  X3 (set-play) is a measured SIGNAL (r=0.721) but is NOT run in
  this build — the arm cap is respected and it is recorded in
  FEATURES for a future prereg.
- Churn/parachute strength is a property of the league, not a
  defect: no arm clamps ratings; the DC fit is allowed its strong
  lambdas for ex-PL clubs, and the virgin calibration leg will
  judge them as they are.
- Halves presentation (all markets): FT + 1H/2H via the frozen
  ENGCH constants, presentation only, exactly as J1.
- Play-off rounds are ordinary rows in every fit (PREPROCESSING
  rule 3); no phase feature is used anywhere.
- Predictions-only: no ENGCH odds/settlement source in-system.
