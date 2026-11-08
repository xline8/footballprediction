# Phase 6 — Model design

## G-PBM — buildable goals candidate

Reference: the production Dixon–Coles goals model as ported in
`league/J1/engine/goals/`, using goals-only observations and `hl = 270`.
The arms are exactly Gate Zero and a pre-registered X2 newcomer-prior arm
using the F4 pooled magnitudes documented in `FEATURES.md`. No other arms are
authorized in Phase A.

Warm-up is 2021. Scored development blocks are 2022–2025, pooled n=1,426.
The virgin window is 2026, n=462, and is read once after preregistration.
The primary line is OU 2.5; its development over-rate is 35.6890%.

Gate legs are: development performance versus league climatology and the
trailing-10 baseline; then, for a dev-passing arm only, virgin log loss must
be no worse than Gate Zero and climatology, and pooled calibration breach
must be ≤1 percentage point for a clean PASS, ≤1 standard error for a
PROVISIONAL PASS, otherwise FAIL. Tie handling and exact arithmetic belong
in the later preregistration.

## Not buildable

S-PBM, C-PBM, K-PBM, and T-PBM are **NOT BUILDABLE**. No valid SOT,
corner, yellow-card, or total-shot target exists in any payload, and no
virgin target window exists for those markets. No engine, fit, prediction,
preregistration, or verdict is produced in Phase A.
