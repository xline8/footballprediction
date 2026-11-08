# Phase 4 — Model Design: BE-FirstDivisionA Candidates

Rules inherited from `league/J1/analysis/MODEL_DESIGN.md`: every
candidate names its production reference, Gate Zero is the
unmodified reference fitted per league, variants come only from
FEATURES.md adopted arms (max 2–3 per candidate), gates are the
program's frozen legs, a FAIL is a complete outcome. Feature
consumption: FEATURES.md.

Shared frame: dev = walk-forward over 2021/2022–2024/2025 (n=1,286,
season-blocked; scored seasons 2022/2023–2024/2025, n=956); virgin =
2025/2026 (n=313, complete), read ONCE and only for arms passing the
dev gate; 2026/2027 reserved un-read as the confirmatory window.
Baselines: league base rate (prior-seasons over-rate at the primary
line) and naive trailing-10 (count markets) / climatology (goals).
Calibration rule: |breach| ≤ 1pp clean PASS; ≤ 1 SE PROVISIONAL
PASS; else FAIL. Primary line per candidate = the .5 line whose dev
over-rate is closest to 0.5.

**Phase rule (frozen here, before any fitting, and repeated in
every prereg):** all phases — regular, championship, Europe,
relegation, final — are ordinary rows in every fit and every window.
The point halving is standings arithmetic and does not touch the
per-match targets; play-off matches are the same squads in the same
competition within weeks; repeated fixtures are already inherent to
the round-robin formats. No phase feature is used anywhere. The
full reasoning and the measured phase levels are in
DATA_UNDERSTANDING §1 and EDA F4.

| Candidate | Reference | Primary line (dev over-rate) | Arms |
|---|---|---|---|
| G-BE goals | production DC + xG blend (model_v2/model_xg pattern) | OU 2.5 (0.551 pooled) + 1X2 LL/RPS | Gate Zero; SHRINK (thin-data prior: ratings of teams with <6 in-league matches shrunk toward league mean — the sanctioned G-J2-lesson arm); X3 set-play decomposition |
| S-BE SOT | model_sot.py v5 | **8.5** (dev 0.547; 9.5 is 0.433 — 8.5 is closer to 0.5) | Gate Zero; RS ratio-shrink (P=20,000); X4 xG/shot quality input (F7 r=0.435, adopted as in S-DK). No X6 (dropped, F8 r=0.075) |
| C-BE corners | model_corners_v3 | **9.5** (dev 0.532; 10.5 is 0.419) | Gate Zero (X9 covariates); X7 box-touch multiplier |
| K-BE cards | model_cards.py | **3.5** (dev 0.543; 4.5 is 0.331) | Gate Zero; X8 referee covariate |
| T-BE total shots | shots family (v1/v2/E9, as T-J1) | **25.5** (dev 0.472; 26.5 is 0.415) | A v1 pattern; B v2 level layer; C E9 trailing-r |

Notes:
- G-BE has xG for every season bar three matches — the blend falls
  back to goals-only exactly three times.
- SHRINK is pre-registered here, before any fitting, per the
  template's explicit sanction; no other rescue arms exist.
- Format breaks: fits are season-blocked expanding windows, so the
  18-team era trains the 16-team era's early fits and never the
  reverse. The 2026/2027 return to 18 teams is in the reserved
  confirmatory window only.
- K-BE's primary line drops to 3.5 (BE yellows level 3.81 is the
  lowest of the European conveyor leagues) and its referee trait is
  the weakest adopted in the program (F9, r=0.378) — recorded in the
  design so a K-BE failure is read correctly.
- S-BE is the only Batch-2 SOT candidate besides DK's to carry the
  X4 arm; its line also drops (8.5, BE SOT level 9.11 with a dev
  over-8.5 rate of 0.547).
- Halves presentation (all markets): FT + 1H/2H via the frozen BE
  constants, presentation only, exactly as J1.
