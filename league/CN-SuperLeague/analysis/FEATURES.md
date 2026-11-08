# Phase A2 — Features

`MODEL_DESIGN.md` may consume only §1 features and the architectural
components in §2. Every feature is causal: for target match M, use only
matches strictly before M; trailing windows require their stated minimum;
ratios are ratios of sums; missing features deactivate the arm rather than
being imputed.

## §1 Adopted

### X1 — Goals-only blend observation pair

Adopted in goals-only form. The corpus has no `expected_goals` key and no
shotmap, so the production blend falls back to official goals. The G-CN
Gate Zero fit uses the production Dixon–Coles pattern with `hl=270`.

### X5 — Trailing target-rate means

Adopted for SOT, corners, stats-feed yellows, total shots, and goals
reference architectures. Dev 2023–2025 reliability is SOT 0.778/0.689
(for/against), corners-for 0.624, total shots 0.742/0.726, goals-for 0.838,
and yellows 0.282/0.347. Cards are weak but X5 still underlies the frozen
cards reference architecture. Trailing windows are strictly pre-match and
need at least six observed values in the ten-match window.

### X7 — Opp-box touches

Adopted only as the C-CN territorial arm: touches-for/against reliability is
0.745/0.620. Coverage is about 55% in 2023 and 100% from 2024. The arm needs
at least eight prior matches with the stat and otherwise falls back to the
corners Gate Zero prediction for that match.

### X9 — Corners Gate Zero territorial pattern

X9 is the corners Gate Zero component: production `corners_v3` covariates
(possession and big chances), carried unchanged as the reference pattern.

## §2 Architectural components

Ratings, home advantage, Dixon–Coles dependence, negative-binomial sizes,
half-share constants, league base rates, and naive baselines are fitted or
harness components, not covariates. The SOT Gate Zero v5 pattern and the
total-shots A/B/E9 patterns are likewise architecture, not new features.

## §3 Rejected / dropped

| Feature | Decision and reason |
|---|---|
| X2 mover tier offset | Dropped for this build. The pre-sanctioned SHRINK arm substitutes for it, following the TH precedent. The descriptive mover check finds 8 team ids first appearing in 2023+, with mean first-season GF gap **−0.3693 goals/match** and GA gap **+0.0891** versus their season mean; details are in `mover_gap.json`. |
| X3 set-play xG split | Dropped: no xG splits exist. |
| X4 xG per shot | Dropped: no shotmap exists. |
| X6 xGOT per shot | Dropped: no xGOT/shotmap exists. |
| X8 referee yellow rate | Dropped: reliability is near zero (block r 0.133/0.014/−0.703; dev 0.218), while coverage collapses to 64.6% in 2025 and 48.75% in the 2026 virgin. |
| Team half-share traits | Rejected: variance ratios 0.95–1.12 are sampling noise; use frozen constants only. |
| Event-unified cards | Sensitivity only; it is not the target because the fit-era stats feed is substantially more consistent. |

## Causality and consumption map

G-CN consumes X1; S-CN consumes the v5 Gate Zero inputs and X5; C-CN uses
X9 in Gate Zero and X7 in its challenger; K-CN uses X5 only; T-CN uses the
shots-family architecture plus trailing-r state as defined in the prereg
family. Referee identity is never used.
