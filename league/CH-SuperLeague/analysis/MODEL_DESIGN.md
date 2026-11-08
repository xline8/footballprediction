# Phase 4 — Model Design: CH-SuperLeague Candidates

Rules inherited from `league/J1/analysis/MODEL_DESIGN.md`: every
candidate names its production reference, Gate Zero is the
unmodified reference fitted per league, variants come only from
FEATURES.md adopted arms (max 2–3 per candidate), gates are the
program's frozen legs, a FAIL is a complete outcome. Feature
consumption: FEATURES.md.

Shared frame: dev = walk-forward over 2021/2022–2024/2025 (n=816,
season-blocked; scored seasons 2022/2023–2024/2025, n=636); virgin =
2025/2026 (n=228, complete), read ONCE and only for arms passing the
dev gate; 2026/2027 reserved un-read as the confirmatory window.
Baselines: league base rate (prior-seasons over-rate at the primary
line) and naive trailing-10 (count markets) / climatology (goals).
Calibration rule: |breach| ≤ 1pp clean PASS; ≤ 1 SE PROVISIONAL
PASS; else FAIL. Primary line per candidate = the .5 line whose dev
over-rate is closest to 0.5.

| Candidate | Reference | Primary line (dev over-rate) | Arms |
|---|---|---|---|
| G-CH goals | production DC + xG blend (model_v2/model_xg pattern) | OU 2.5 (0.565 pooled) + 1X2 LL/RPS | Gate Zero; SHRINK (thin-data prior: ratings of teams with <6 in-league matches shrunk toward league mean — the sanctioned G-J2-lesson arm); X3 set-play decomposition |
| S-CH SOT | model_sot.py v5 | 9.5 (dev 0.463) | Gate Zero; RS ratio-shrink (P=20,000). **No X4 arm** (FEATURES: r=0.247 failed the arm standard); no X6 (dropped) |
| C-CH corners | model_corners_v3 | **10.5** (dev 0.447; 9.5 is 0.561 — 10.5 is closer to 0.5) | Gate Zero (X9 covariates); X7 box-touch multiplier |
| K-CH cards | model_cards.py | **4.5** (dev 0.467; 3.5 is 0.669) | Gate Zero; X8 referee covariate |
| T-CH total shots | shots family (v1/v2/E9, as T-J1) | 26.5 (dev 0.518) | A v1 pattern; B v2 level layer; C E9 trailing-r |

Notes:
- G-CH has xG for every season bar one match — the blend falls back
  to goals-only exactly once (match 4201311).
- SHRINK is pre-registered here, before any fitting, per the
  template's explicit sanction; no other rescue arms exist.
- Format break: fits are season-blocked expanding windows, so the
  10-team era trains the 12-team era's early fits and never the
  reverse. Split rounds are ordinary rows in every fit
  (PREPROCESSING rule 3); no phase feature is used anywhere.
- K-CH's team trait is weak in this league (F2, r=0.256) — recorded
  in the design so a K-CH failure is read correctly: the candidate
  stands or falls mainly on X8 and the baselines.
- Halves presentation (all markets): FT + 1H/2H via the frozen CH
  constants, presentation only, exactly as J1.
