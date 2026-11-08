# Phase 4 — Model Design: DK-Superligaen Candidates

Rules inherited from `league/J1/analysis/MODEL_DESIGN.md`: every
candidate names its production reference, Gate Zero is the unmodified
reference fitted per league, variants come only from FEATURES.md
adopted arms (max 2–3 per candidate), gates are the program's frozen
legs, a FAIL is a complete outcome. Feature consumption: FEATURES.md.

Shared frame: dev = walk-forward over 2021/2022–2024/2025 (n=772,
season-blocked); virgin = 2025/2026 (n=193, complete), read ONCE and
only for arms passing the dev gate; 2026/2027 reserved un-read as
the confirmatory window. Baselines: league base rate (prior-seasons
over-rate at the primary line) and naive trailing-10 (count markets)
/ climatology (goals). Calibration rule: |breach| ≤ 1pp clean PASS;
≤ 1 SE PROVISIONAL PASS; else FAIL. Primary line per candidate =
the .5 line whose dev over-rate is closest to 0.5.

| Candidate | Reference | Primary line (dev over-rate) | Arms |
|---|---|---|---|
| G-DK goals | production DC + xG blend (model_v2/model_xg pattern) | OU 2.5 (0.552 pooled) + 1X2 LL/RPS | Gate Zero; SHRINK (thin-data prior: ratings of teams with <6 in-league matches shrunk toward league mean — the sanctioned G-J2-lesson arm); X3 set-play decomposition |
| S-DK SOT | model_sot.py v5 | 9.5 (dev 0.446) | Gate Zero; RS ratio-shrink (P=20,000); X4 xG/shot quality input |
| C-DK corners | model_corners_v3 | 9.5 (dev 0.539) | Gate Zero (X9 covariates); X7 box-touch multiplier |
| K-DK cards | model_cards.py | 3.5 (dev 0.474) | Gate Zero; X8 referee covariate |
| T-DK total shots | shots family (v1/v2/E9, as T-J1) | 25.5 (dev 0.506) | A v1 pattern; B v2 level layer; C E9 trailing-r |

Notes:
- G-DK has xG for every season — the blend never falls back to
  goals-only (contrast J1 2021).
- SHRINK is pre-registered here, before any fitting, per the
  template's explicit sanction; no other rescue arms exist.
- X6 (xGOT) is absent by FEATURES verdict (F7 fail) — S-DK runs
  three arms, not four.
- Halves presentation (all markets): FT + 1H/2H via the frozen DK
  constants, presentation only, exactly as J1.
- Split rounds and the playoff final are ordinary rows in every fit
  (PREPROCESSING rule 3); no phase feature is used anywhere.
