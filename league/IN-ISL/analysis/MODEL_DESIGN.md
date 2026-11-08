# Phase 4 — Model Design: IN-ISL Candidates

Rules inherited from `league/J1/analysis/MODEL_DESIGN.md`: every
candidate names its production reference, Gate Zero is the
unmodified reference fitted per league, variants come only from
FEATURES.md adopted arms (max 2–3 per candidate), gates are the
program's frozen legs, a FAIL is a complete outcome. Feature
consumption: FEATURES.md.

Shared frame: dev = walk-forward over 2021/2022–2024/2025
(n=534; scored pool n=419 for both the season-blocked goals
design and the per-match designs, warm-up season 2021/2022),
virgin = 2025/2026 (n=91, complete — a truncated single
round-robin; see DATA_UNDERSTANDING §1), read ONCE and only
for arms passing the dev gate; 2026/2027 reserved un-read as
the confirmatory window (season-end confirmatory read when it
completes).
Baselines: league base rate (prior-seasons over-rate at the
primary line) and naive trailing-10 (count markets) /
climatology (goals). Calibration rule: |breach| ≤ 1pp clean
PASS; ≤ 1 SE PROVISIONAL PASS; else FAIL. Primary line per
candidate = the .5 line whose dev over-rate is closest to 0.5.
Phase rule (FREEZE): play-off matches are ordinary rows in
every fit (DATA_UNDERSTANDING §1); no phase feature anywhere.

| Candidate | Reference | Primary line (dev over-rate) | Arms |
|---|---|---|---|
| G-IN goals | production DC + xG blend (model_v2/model_xg pattern) | OU 2.5 (0.563 pooled) + 1X2 LL/RPS | Gate Zero; SHRINK (thin-data prior: ratings of teams with <6 in-league matches shrunk toward league mean — the sanctioned G-J2-lesson arm; Inter Kashi + SC Delhi debut in the virgin, Punjab/Mohammedan in dev); X3 set-play decomposition |
| S-IN SOT | model_sot.py v5 | 8.5 (dev 0.461) | Gate Zero; RS ratio-shrink (P=20,000); X4 xG/shot quality input (X6 DROPPED in FEATURES: era = one dev season, trait weak) |
| C-IN corners | model_corners_v3 | 10.5 (dev 0.444; 9.5 is 0.558 — 10.5 is closer to 0.5 by 0.002) | Gate Zero (X9 covariates); X7 box-touch multiplier |
| K-IN cards | model_cards.py | 4.5 (dev events 0.439) | Gate Zero ONLY (X8 dropped in FEATURES: referee coverage 13.5% dev / 0% virgin, trait not computable). Target = EVENT-UNIFIED yellows (Phase 1 §3 decision) |
| T-IN total shots | shots family (v1/v2/E9, as T-J1) | 26.5 (dev 0.468) | A v1 pattern; B v2 level layer; C E9 trailing-r |

Notes:
- G-IN has xG for every season — the blend never falls back to
  goals-only (contrast J1 2021). The F11 scale caveat
  (goals/xG ≈ 1.19) is recorded against the candidate in
  advance; Gate Zero stays the unmodified pattern.
- SHRINK is pre-registered here, before any fitting, per the
  template's explicit sanction; no other rescue arms exist.
- K-IN's single-arm form is a FEATURES consequence, not a
  shortcut: with X8 dropped there is no adopted variant to run.
  Its gate is unchanged (Gate Zero must beat both baselines on
  dev and pass the virgin legs alone).
- S-IN's three-arm form is likewise a FEATURES consequence
  (X6 dropped on era + reliability, F7).
- Halves presentation (all markets): FT + 1H/2H via the frozen
  IN constants, presentation only, exactly as J1.
- Thin-league warning (F12): dev scored pool n=419, virgin
  n=91 — the smallest virgin in the program. SEs are reported
  mechanically; no gate is loosened because of pool size.
