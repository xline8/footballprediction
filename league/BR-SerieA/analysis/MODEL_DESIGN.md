# Phase 4 — Model Design: BR-SerieA Candidates

Rules inherited from `league/J1/analysis/MODEL_DESIGN.md`: every
candidate names its production reference, Gate Zero is the
unmodified reference fitted per league, variants come only from
FEATURES.md adopted arms (max 2–3 per candidate), gates are the
program's frozen legs, a FAIL is a complete outcome. Feature
consumption: FEATURES.md.

Shared frame: dev = walk-forward over 2021–2024 (warm-up 2021,
scored 2022–2024, n=1,140, season-blocked); virgin = **2025
(n=380, complete)**, read ONCE and only for arms passing the dev
gate; 2026 partial (n=339) reserved un-read as the confirmatory
window. Baselines: league base rate (prior-seasons over-rate at
the primary line) and naive trailing-10 (count markets) /
climatology (goals). Calibration rule: |breach| ≤ 1pp clean PASS;
≤ 1 SE PROVISIONAL PASS; else FAIL. Primary line per candidate =
the .5 line whose dev over-rate is closest to 0.5.

| Candidate | Reference | Primary line (dev over-rate) | Arms |
|---|---|---|---|
| G-BR goals | production DC + xG blend (model_v2/model_xg pattern) | OU 2.5 (0.452 pooled) + 1X2 LL/RPS | Gate Zero; SHRINK (thin-data prior); X2 mover tier offset; X3 set-play decomposition |
| S-BR SOT | model_sot.py v5 | 8.5 (dev 0.544) | Gate Zero; RS ratio-shrink (P=20,000); X4 xG/shot quality input |
| C-BR corners | model_corners_v3 | 10.5 (dev 0.476) | Gate Zero (X9 covariates); X7 box-touch multiplier |
| K-BR cards | model_cards.py | 4.5 unified (dev 0.573) | Gate Zero; X8 referee covariate |
| T-BR total shots | shots family (v1/v2/E9, as T-J1) | 26.5 (dev 0.520) | A v1 pattern; B v2 level layer; C E9 trailing-r |

Notes:
- G-BR is the program's first goals candidate where **both** the
  X2 mover offset is estimable (Série B in-corpus) *and* the
  SHRINK lesson applies (4 promoted sides/season). They are
  separate arms; the prereg freezes how each is parameterised and
  forbids stacking.
- G-BR's blend is goals-only in effect until 2023 (xG coverage
  ~7–10% in 2021/2022) and a true blend from 2023 — the reference
  pattern's own fallback, not a design change. X3 likewise can
  only activate once xG windows fill (2023+ dev).
- S-BR runs three arms, not four: X6 is DROPPED at FEATURES
  (its era is the virgin season itself — untestable in dev).
- K-BR's target is the **unified** yellows (events 2021–2022,
  stats 2023+; PREPROCESSING). The stats-feed-only level break is
  a feed artefact and must not leak into the target.
- Halves presentation (all markets): FT + 1H/2H via the frozen BR
  constants (goals 0.455, SOT 0.462, corners 0.474, shots 0.463,
  yellows 0.366), presentation only, exactly as J1.
- No phase/format features exist to use: the competition is a
  single round-robin table from round 1 to 38.
