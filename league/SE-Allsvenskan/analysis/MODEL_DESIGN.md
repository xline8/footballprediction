# Phase 4 — Model Design: SE-Allsvenskan Candidates

Rules inherited from `league/J1/analysis/MODEL_DESIGN.md`: every
candidate names its production reference, Gate Zero is the unmodified
reference fitted per league, variants come only from FEATURES.md
adopted arms (max 2–3 per candidate), gates are the program's frozen
legs, a FAIL is a complete outcome. Feature consumption: FEATURES.md.

Shared frame: dev = walk-forward over 2021–2024 (n=960,
season-blocked); virgin = 2025 (n=240, complete), read ONCE and
only for arms passing the dev gate; 2026 (224/240 at pull) reserved
un-read as the confirmatory window. Baselines: league base rate
(prior-seasons over-rate at the primary line) and naive trailing-10
(count markets) / climatology (goals). Calibration rule: |breach|
≤ 1pp clean PASS; ≤ 1 SE PROVISIONAL PASS; else FAIL. Primary line
per candidate = the .5 line whose dev over-rate is closest to 0.5.

| Candidate | Reference | Primary line (dev over-rate) | Arms |
|---|---|---|---|
| G-SE goals | production DC + xG blend (model_v2/model_xg pattern) | OU 2.5 (0.531 pooled) + 1X2 LL/RPS | Gate Zero; SHRINK (thin-data prior: ratings of teams with <6 in-league matches shrunk toward league mean — the sanctioned G-J2-lesson arm); X3 set-play decomposition |
| S-SE SOT | model_sot.py v5 | 8.5 (dev 0.531) | Gate Zero; RS ratio-shrink (P=20,000); X4 xG/shot quality input |
| C-SE corners | model_corners_v3 | 10.5 (dev 0.492) | Gate Zero (X9 covariates); X7 box-touch multiplier |
| K-SE cards | model_cards.py | 3.5 (dev 0.448) | Gate Zero; X8 referee covariate |
| T-SE total shots | shots family (v1/v2/E9, as T-J1) | 26.5 (dev 0.514) | A v1 pattern; B v2 level layer; C E9 trailing-r |

Notes:
- G-SE has xG for every season — the blend never falls back to
  goals-only (contrast J1 2021).
- SHRINK is pre-registered here, before any fitting, per the
  template's explicit sanction; X2 (tier offset) is inestimable in
  this corpus (FEATURES) and no other rescue arms exist.
- X6 (xGOT) is absent by FEATURES verdict (F7 fail) — S-SE runs
  three arms, not four.
- K-SE's X8 arm carries SE's coverage caveat: referee identity is
  unknown for all of 2021 (the warm-up season) and 12–29% of later
  matches; those fixtures use the base form (fallback, no
  imputation), exactly as the DK/NL harnesses record fallbacks.
- Halves presentation (all markets): FT + 1H/2H via the frozen SE
  constants, presentation only, exactly as J1.
- No phase feature is used anywhere: the season is a straight
  double round robin with no split rounds.
