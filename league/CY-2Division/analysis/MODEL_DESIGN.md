# Model design — Cyprus 2. Division

This document freezes data and pre-registration only. No fitting is
performed here. One candidate is buildable in this league (EDA F5):
**G-CY2, goals**. SOT / corners / total shots have no target in the
data; cards have no yellow target; referee / xG / shotmap / lineups
are absent. The goals candidate follows the CY-1Division analogue
architecture (production Dixon-Coles pattern, goals-only) with CY-2
rows, windows, primary line, and source decisions substituted.

## Candidate G-CY2 — goals model (1X2 / OU / BTTS / DC)

(a) **Reference**: the production goals model — Dixon-Coles fit as
used market-free in the experiments (per-division rho, goals-only
observations, exponential time decay), and its walk-forward
harness; as implemented for sibling G-CY
(`league/CY-1Division/engine/goals/`).

(b) **Identical**: DC estimation pattern and rho grid; Poisson
family with DC low-score correction; time-decay fitting (half-life
270 days, frozen); the walk-forward evaluation harness and its
log-loss/RPS + calibration gate legs. No xG exists, so the blend
degrades to goals-only throughout (the reference's own documented
fallback, not a new design).

(c) **EDA-justified changes**:
  1. *Cross-tier prior for relegated-in clubs* (feature **X2**,
     EDA F4). A club whose immediately-preceding season was in
     CY-1Division enters CY-2 with a rating offset of attack
     **+0.08** / defence **−0.21** goals per match (measured gap,
     n = 8 team-seasons, defence-led) — applied at prediction time
     in the arrival season only, added to the fitted rating exactly
     as the J1 X2 arm specifies. Brand-new ids (no CY-1/CY-2
     previous season) start at the league mean in every arm.
  2. *Variant arm: SHRINK* (the G-J2 post-mortem arm). Ratings of
     teams with fewer than 6 training-window matches are shrunk
     toward the league mean by factor counts/6 — guarding against
     extreme lambdas for thin-history teams in season openers.
     Expected to coincide with Gate Zero in this league (every
     non-new team has ~30 training matches; new teams are already
     at the mean); run anyway, gated like any arm.

(d) **Forbidden here**: half-share anything (F3); finishing/form
features; standings/h2h snapshots as features (post-match
leakage); any use of the `yellow_*` column as a target (it counts
second-yellow dismissals only — F5); any phase feature.

**NOT built if**: the dev walk-forward gate fails — the model
stands or falls on its own gate; a CY-1Division pass confers
nothing here.

## Shared validation frame

- **Dev period** (walk-forward, expanding window, season-blocked):
  seed 2021/2022; scored seasons 2022/2023, 2023/2024, 2024/2025
  (pooled dev n = 682).
- **Virgin window, evaluated once, after the design is frozen**:
  2025/2026 (n = 232, complete), with 2026/2027 reserved as the
  confirmatory virgin window, evaluated once when complete.
- Design-level aggregates were inspected across all seasons during
  EDA (that is what EDA is); the virgin window is virgin for
  fitting, feature selection among arms, and gate setting. No
  parameter may be tuned on it. (The X2 magnitudes were measured
  on pre-virgin transitions only — 2022/2023–2024/2025 arrivals —
  so no virgin-season information enters the design.)
- Baselines: climatology (pooled outcome rates and OU2.5 over-rate
  of all seasons strictly before the target season).
- **Gate Zero**: the unmodified reference architecture, fitted per
  league, is itself an arm. A candidate whose justified changes do
  not beat (or at least match within the both-pass rule) its own
  reference arm does not ship its changes.
- Both-pass rule: if base arm and variant arm both pass the gate
  legs (log-loss leg + calibration leg at ±1.0pp pooled on the
  virgin window, per-season sign check), the arm with the lower
  pooled virgin 1X2 LL ships.

## Halves presentation

FT + 1H/2H via the frozen CY-2 goals constant **0.4351** (EDA F3),
presentation only — never fitted, never a per-team quantity.
