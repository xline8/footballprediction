# Phase 4 — Model Design: SCO-Premiership Candidates

Rules inherited from `league/J1/analysis/MODEL_DESIGN.md`: every
candidate names its production reference, Gate Zero is the unmodified
reference fitted per league, variants come only from FEATURES.md
adopted arms (max 2–3 per candidate), gates are the program's frozen
legs, a FAIL is a complete outcome. Feature consumption: FEATURES.md.

Shared frame: dev = walk-forward over 2021/2022–2024/2025 (train seed
2021/2022; evaluation 2022/2023–2024/2025, pooled n=684,
season-blocked); virgin = 2025/2026 (n=228, complete), read ONCE and
only for arms passing the dev gate; 2026/2027 (partial, n=75)
reserved un-read as the confirmatory window. Baselines: league base
rate (prior-seasons over-rate at the primary line) and naive
trailing-10 (count markets) / climatology (goals). Calibration
rule: |breach| ≤ 1pp clean PASS; ≤ 1 SE PROVISIONAL PASS; else FAIL.
Primary line per candidate = the .5 line whose dev over-rate is
closest to 0.5.

| Candidate | Reference | Primary line (dev over-rate) | Arms |
|---|---|---|---|
| G-SCO goals | production DC + xG blend (model_v2/model_xg pattern) | OU 2.5 (0.538 pooled) + 1X2 LL/RPS | Gate Zero; SHRINK (thin-data prior — sanctioned G-J2-lesson arm); X3 set-play decomposition |
| S-SCO SOT | model_sot.py v5 | 8.5 (dev 0.457) | Gate Zero; RS ratio-shrink; X4 xG/shot quality input. (X6 xGOT adopted in FEATURES but its population era starts 2024/2025, inside the last dev season — the arm could never be honestly dev-tested across the dev window, so it is NOT run in this build; recorded here as the BR X6 lesson applied in advance.) |
| C-SCO corners | model_corners_v3 | 10.5 (dev 0.496) | Gate Zero (X9 covariates); X7 box-touch multiplier |
| K-SCO cards | model_cards.py | 3.5 (dev 0.521) | Gate Zero only (X8 dropped in FEATURES, r=0.158) |
| T-SCO total shots | shots family (v1/v2/E9, as T-J1) | 24.5 (dev 0.516) | A v1 pattern; B v2 level layer; C E9 trailing-r |

Notes:
- G-SCO has xG for every season — the blend never falls back to
  goals-only (contrast J1 2021).
- SHRINK is pre-registered here, before any fitting, per the
  template's explicit sanction; no other rescue arms exist.
- Old Firm dominance is a property of the league, not a defect:
  no arm clamps ratings; the DC fit is allowed its extreme lambdas,
  and the virgin calibration leg will judge them as they are.
- Halves presentation (all markets): FT + 1H/2H via the frozen SCO
  constants, presentation only, exactly as J1.
- Split rounds are ordinary rows in every fit (PREPROCESSING rule
  3); no phase feature is used anywhere.
- Predictions-only: no SCO odds/settlement source in-system.
