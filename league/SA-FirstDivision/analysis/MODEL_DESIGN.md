# Phase 4 — Model Design: SA-FirstDivision Candidates

Rules inherited from `league/J1/analysis/MODEL_DESIGN.md`: every
candidate names its production reference, Gate Zero is the
unmodified reference fitted per league, variants come only from
FEATURES.md adopted arms (max 2–3 per candidate), gates are the
program's frozen legs, a FAIL is a complete outcome. Feature
consumption: FEATURES.md.

## Shared frame — a thin corpus, two dev seasons

- **Goals:** dev = within-season walk-forward over 2024/2025
  regular played (warm-up first 90 matches by date, scored
  remaining **n=216**); virgin = 2025/2026 regular played
  (**n=304**, complete). 2026/2027 is the reserved confirmatory
  window for goals and is NOT read in this build.
- **SOT / corners / cards / total shots:** dev = within-season
  walk-forward over 2025/2026 regular played (warm-up first 90,
  scored remaining **n=214**); virgin = 2026/2027 partial
  (**n=94**, rounds 1–11, **TRANSITIONAL** — confirmatory read at
  season end). There is no earlier stats season: 2024/2025 is
  score-only, so no count-market dev can predate 2025/2026.
- **Frozen exclusions (PREPROCESSING.md):** promotion playoffs (3
  per complete season) and the 2 awarded 2025/2026 matches are
  excluded from every fit and scored window.
- Baselines: league base rate (prior-history over-rate at the primary
  line) and naive trailing-10 (count markets) / climatology (goals).
  For the within-season dev, climatology/base rate for a scored
  match is computed from matches strictly before it (expanding), so
  no scored match ever informs its own baseline.
- Calibration rule: |breach| ≤ 1pp clean PASS; ≤ 1 SE PROVISIONAL
  PASS; else FAIL. Calibration convention: actual minus predicted.
- Primary line per candidate = the .5 line whose **dev**
  (full dev regular-played season) over-rate is closest to 0.5
  (EDA.md, F1 / dev_lines).

| Candidate | Reference | Primary line (dev over-rate) | Arms |
|---|---|---|---|
| G-SAFD goals | production DC + xG blend, goals-only (model_v2/model_xg pattern) | OU 2.5 (0.500) + 1X2 LL/RPS | Gate Zero; SHRINK (thin-data prior — sanctioned G-J2-lesson arm) |
| S-SAFD SOT | model_sot.py v5 | 8.5 (0.487) | Gate Zero; RS ratio-shrink |
| C-SAFD corners | model_corners_v3 | 9.5 (0.434) | Gate Zero (X9 covariates); X7 box-touch multiplier |
| K-SAFD cards | model_cards.py | 4.5 (0.470) | Gate Zero only (X8 dropped in FEATURES: referee 0% in dev). Target = unified event yellows |
| T-SAFD total shots | shots family (v1/v2/E9, as T-J1) | 23.5 (0.487) | A v1 pattern; B v2 level layer; C E9 trailing-r |

Notes:
- G-SAFD's blend is goals-only in every window (no xG anywhere —
  FEATURES X1). The SHRINK arm is pre-registered here, before any
  fitting, per the template's explicit sanction; with 6-team churn
  per season, thin-data newcomers are a structural feature of this
  league. No other rescue arms exist.
- S-SAFD's X4/X6 arms do not exist (no shotmap/xGOT — FEATURES).
  The RS arm is the only ratio test, per §2 of FEATURES.md.
- C-SAFD's X7 arm is live on EDA evidence (box-touch for-trait
  r=0.790; per-match corr with corners 0.537, above J1's 0.471).
- K-SAFD's team trait is noise (yellows-for r=0.156, F2) — the dev
  gate is expected to be hard, exactly as K-SA's was. No arm can
  manufacture a trait that is not there.
- T-SAFD's E9 arm (trailing-r dispersion) is the same challenger
  family as the top-5 prospective test; here it is a pre-registered
  dev arm like any other, judged by the same gate.
- Halves presentation: G-SAFD FT only (no goals 1H constant —
  F3). S/C/T/K: FT + 1H/2H via the frozen 2025/2026 constants
  (SOT 0.4540, corners 0.4678, total shots 0.4557, event yellows
  0.4010), presentation only, exactly as J1.
- Predictions-only: no SA-FirstDivision odds/settlement source
  in-system.
