# Phase 4 — Model Design: AU-ALeague Candidates

Rules inherited from `league/J1/analysis/MODEL_DESIGN.md`: every
candidate names its production reference, Gate Zero is the
unmodified reference fitted per league, variants come only from
FEATURES.md adopted arms (max 2–3 per candidate), gates are the
program's frozen legs, a FAIL is a complete outcome. Feature
consumption: FEATURES.md.

Shared frame: dev = walk-forward over 2021/2022–2024/2025
(n=671; scored pool n=508 for the season-blocked goals design,
warm-up season 2021/2022 for the per-match designs), virgin =
2025/2026 (n=163, complete — see DATA_UNDERSTANDING §4 for the
brief-vs-warehouse note), read ONCE and only for arms passing
the dev gate; 2026/2027 reserved un-read as the confirmatory
window (season-end confirmatory read when it completes).
Baselines: league base rate (prior-seasons over-rate at the
primary line) and naive trailing-10 (count markets) /
climatology (goals). Calibration rule: |breach| ≤ 1pp clean
PASS; ≤ 1 SE PROVISIONAL PASS; else FAIL. Primary line per
candidate = the .5 line whose dev over-rate is closest to 0.5.

| Candidate | Reference | Primary line (dev over-rate) | Arms |
|---|---|---|---|
| G-AU goals | production DC + xG blend (model_v2/model_xg pattern) | OU 2.5 (0.608 pooled) + 1X2 LL/RPS | Gate Zero; SHRINK (thin-data prior: ratings of teams with <6 in-league matches shrunk toward league mean — the sanctioned G-J2-lesson arm; Auckland FC's 2024/2025 entry is the live case); X3 set-play decomposition |
| S-AU SOT | model_sot.py v5 | 9.5 (dev 0.529) | Gate Zero; RS ratio-shrink (P=20,000); X4 xG/shot quality input; X6 xGOT era-guarded input |
| C-AU corners | model_corners_v3 | 10.5 (dev 0.511) | Gate Zero (X9 covariates); X7 box-touch multiplier |
| K-AU cards | model_cards.py | 3.5 (dev 0.537) | Gate Zero ONLY (X8 dropped in FEATURES: referee trait r=0.06, coverage 82.8% in virgin) |
| T-AU total shots | shots family (v1/v2/E9, as T-J1) | 27.5 (dev 0.541) | A v1 pattern; B v2 level layer; C E9 trailing-r |

Notes:
- G-AU has xG for every season — the blend never falls back to
  goals-only (contrast J1 2021).
- SHRINK is pre-registered here, before any fitting, per the
  template's explicit sanction; no other rescue arms exist.
- K-AU's single-arm form is a FEATURES consequence, not a
  shortcut: with X8 dropped there is no adopted variant to run.
  Its gate is unchanged (Gate Zero must beat both baselines on
  dev and pass the virgin legs alone).
- Halves presentation (all markets): FT + 1H/2H via the frozen
  AU constants, presentation only, exactly as J1.
- Finals Series matches are ordinary rows in every fit
  (PREPROCESSING rule 3); no phase feature is used anywhere.
- Small-n warning (F12): dev scored pool n=508, virgin n=163 —
  the smallest in the conveyor so far. SEs are reported
  mechanically; no gate is loosened because of pool size.
