# Step 6 — Model Design: GE-Erovnuli

## Feasibility matrix

| candidate | target exists? | virgin window has target? | verdict |
|---|---|---|---|
| G-GE goals | YES (scores 1,059/1,059) | YES (2025, n=180) | **BUILD** |
| S-GE SOT | NO (stats null, shotmap empty) | — | not buildable |
| C-GE corners | NO (no source) | — | not buildable |
| K-GE cards | NO (fragmentary events only) | — | not buildable |
| T-GE total shots | NO (shotmap empty) | — | not buildable |

## Candidate G-GE — goals model (FT 1X2 / OU / BTTS / DC)

- **Reference**: production Dixon-Coles (`model_v2.py` pattern), as
  in PREREG_G_J1/G_J2: iterative multiplicative updates, 14 sweeps,
  damping 0.7, +0.25 smoothing, fitted home advantage (init 0.28),
  rho per fit from grid (0.0, −0.05, −0.10, −0.15) by weighted fit LL,
  score matrix to MAXG = 10, exponential time decay half-life 270 d
  (production value, frozen).
- **Observation**: goals-only (X1 reduced — the blend's documented
  fallback; no xG exists).
- **Arms** (max per template): (1) Gate Zero — unmodified reference,
  unseen teams at league mean; (2) SHRINK — Gate Zero + the FEATURES
  shrinkage for 1–5-prior-match teams. No other arms; no rescue arms.
- **Evaluation**: season-blocked expanding walk-forward exactly as
  PREREG_G_IN: seed 2021, evaluation seasons 2022, 2023, 2024 pooled;
  one fit per target season on all matches strictly before that
  season's first match date. Primary line OU 2.5 (dev OU2.5 rate
  ≈ 0.52 — the median line). Metrics: 1X2 LL, RPS, OU2.5 LL vs
  climatology/base-rate baselines computed from seasons strictly
  before the target season.
- **Virgin**: 2025 (n=180), read ONCE, only for dev-passing arms,
  fit on all matches before the first 2025 match date.
- **Gate legs**: identical verbatim legs to PREREG_G_J1/G_IN (dev
  gate vs baselines; virgin LL leg vs Gate Zero + climatology;
  calibration leg |breach| ≤ 1.0pp clean, ≤1 SE provisional, else
  FAIL; per-season sign check leg (iii) for variants; both-pass rule
  → lower pooled virgin 1X2 LL ships, ties to the simpler arm).
- **Halves**: presentation only via frozen constant 0.4516 (F3).
- **Forbidden**: half-share fitting, mover offsets (no feeder data),
  any feature not in FEATURES §adopted, post-hoc arms.
