# KW-PremierLeague — Model Design (Step 6)

Per candidate: reference pattern, what stays identical, what this
league's EDA justifies changing, arms, baselines. Design consumes
only Step-5 features (FEATURES.md).

## G-KW (goals) — BUILDABLE

- Reference pattern: programme Dixon-Coles (FI G analogue, BY port):
  iterative sweep optimiser, 14 sweeps, damping 0.7, +0.25 smoothing,
  home init 0.28, MAXG = 10, production tau, rho grid
  (0.0, −0.05, −0.10, −0.15) by goals log-likelihood, decay
  half-life 270 days. Carried over verbatim (dc.py).
- Identical: fit mechanics, season-blocked expanding evaluation,
  baselines, gate legs (frozen verbatim in PREREG_G_KW.md).
- League-specific: (a) observation is goals-only in every match
  (X1 fallback — no xG exists, EDA F1); (b) warm-up season is the
  calendar season "2021" (n=64) and the scored dev window is FOUR
  seasons (2021/2022–2024/2025, pooled n=422) — one more dev season
  than the recent 3-season leagues, because the split gives a
  complete extra season before the virgin; (c) entrant offsets use
  the ordered season list (labels are not integers).
- Arms: **Gate Zero** (unmodified reference), **SHRINK** (n<6
  exponent scaling — expected near-inert, see FEATURES), **X2**
  (SHRINK + entrant tilt, EDA F4).
- Baselines: climatology (pooled prior-season H/D/A rates + OU2.5
  over-rate) and naive trailing-10 (per-team trailing-10 goals-for
  means, independent Poissons, no home advantage) — both frozen.
- Virgin: 2025/2026 (n=111), read once, only if Gate Zero passes
  the dev gate; 2026/2027 untouched.

## S-KW (shots on target) — NOT-BUILDABLE

No stats feed in any season (0/711), no shotmap substitute: no SOT
target exists in the dev era or any era (EDA F1). No engine, no
prereg beyond the not-buildable record.

## C-KW (corners) — NOT-BUILDABLE

Same absence: no corners target in any season under any source;
X7 input also absent (EDA F1).

## K-KW (cards) — NOT-BUILDABLE

No yellows target under either source in any season: stats feed
absent everywhere; event feed carries ZERO plain Yellow and ZERO
YellowRed events in the entire corpus (only 53 straight Reds).
Referee coverage 0% — no X8 arm (EDA F5). Strongest K not-buildable
case in the programme alongside CN.

## T-KW (total shots) — NOT-BUILDABLE

No total-shots target in any season; shotmap empty everywhere
(EDA F1).
