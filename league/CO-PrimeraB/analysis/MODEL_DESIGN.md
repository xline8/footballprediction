# Step 6 — Model Design: CO-PrimeraB

## Feasibility matrix

| candidate | target exists? | virgin window has target? | verdict |
|---|---|---|---|
| G-CO goals | YES (scores 1,639/1,639 finished) | YES (2025, n=308) | **BUILD** |
| S-CO SOT | NO (stats null, shotmap empty) | — | not buildable |
| C-CO corners | NO (no source) | — | not buildable |
| K-CO cards | NO (events fragmentary in dev+virgin; complete-looking only in in-progress 2026, which has no fittable history) | — | not buildable |
| T-CO total shots | NO (shotmap empty) | — | not buildable |

## Candidate G-CO — goals model (FT 1X2 / OU / BTTS / DC)

- **Reference**: production Dixon-Coles (`model_v2.py` pattern), as
  in PREREG_G_GE / PREREG_G_BG2: iterative multiplicative updates,
  14 sweeps, damping 0.7, +0.25 smoothing, fitted home advantage
  (init 0.28), rho per fit from grid (0.0, −0.05, −0.10, −0.15) by
  weighted fit LL, score matrix to MAXG = 10, exponential time decay
  half-life 270 d (production value, frozen).
- **Observation**: goals-only (X1 reduced — the blend's documented
  fallback; no xG exists).
- **Season unit**: the calendar year (warehouse label), containing
  the Apertura + Clausura tournaments and all their phases (frozen
  phase rule: all phases modelled, phase flagged, no phase feature).
- **Arms** (3, the template maximum): (1) Gate Zero — unmodified
  reference, unseen teams at league mean; (2) SHRINK — Gate Zero +
  the FEATURES shrinkage for 1–5-prior-match teams (live in this
  league via the partial 2021 seed); (3) X2 — Gate Zero + the
  FEATURES cross-tier mover prior for relegated-from-Primera-A
  clubs (frozen offsets a = ln 1.10, d = ln 0.73 replacing fitted
  ratings in the club's first B season). No other arms; no rescue
  arms.
- **Evaluation**: season-blocked expanding walk-forward exactly as
  PREREG_G_GE: seed 2021 (partial, training only), evaluation
  seasons 2022, 2023, 2024 pooled (n = 909); one fit per target
  season on all matches strictly before that season's first match
  date. Primary line OU 2.5 (dev OU2.5 rate ≈ 0.39–0.43 — the
  median line). Metrics: 1X2 LL, RPS, OU2.5 LL vs climatology /
  base-rate baselines computed from seasons strictly before the
  target season, plus a naive trailing-10 baseline reported for
  context (NOT a gate leg; formula frozen in the prereg).
- **Virgin**: 2025 (n = 308, last complete calendar year), read
  ONCE, only for dev-passing arms, fit on all matches before the
  first 2025 match date.
- **Gate legs**: identical verbatim legs to PREREG_G_GE / G_BG2
  (dev gate vs baselines; virgin LL leg vs Gate Zero + climatology;
  calibration leg |breach| ≤ 1.0pp clean, ≤1 SE provisional, else
  FAIL; per-season sign check leg (iii) for variants; both-pass rule
  → lower pooled virgin 1X2 LL ships, ties to the simpler arm).
- **Halves**: presentation only via frozen constant 0.4875 (F3).
- **Forbidden**: half-share fitting, any feature not in FEATURES
  §adopted, phase filtering/features, post-hoc arms, reading 2026.
