# Phase 3.5 — Feature Engineering: IE-PremierDivision

The J1 causality contract applies: strictly pre-match trailing or expanding
windows, ratio-of-sums for ratios, minimum eight observations where stated,
NaN means inactive, and no 2026 design input.

| Feature | IE verdict | Evidence / decision |
|---|---|---|
| X1 goals + xG observation pair | **ADOPTED goals-only** | xG exists only in 2025–2026: one dev season plus the virgin. The blend cannot be dev-validated, so the goals model is goals-only and the virgin's xG is never used |
| X2 mover tier offset | **DROPPED** | The mover check records about one transition per season; the SHRINK arm covers new-team failure mode |
| X3 set-play xG | **DROPPED** | xG split era is 2025+ only |
| X4 xG/shot | **DROPPED** | shotmap xG era is 2025+ only; one dev season |
| X5 trailing target means | **ADOPTED** | stats targets from 2022+, event cards from 2021+ |
| X6 xGOT | **DROPPED** | 2025+ only; one dev season |
| X7 box touches | **ADOPTED** corners variant | partial 2022–2023 coverage, complete from 2024; min-8 inactivity rule |
| X8 referee | **DROPPED** | event-yellows referee r is recorded in JSON and is below 0.40 |
| X9 possession + big chance | **ADOPTED** | corners Gate Zero covariates |

First-half shares are frozen constants, not team features. Lineups, standings,
h2h, attendance, game-state variables and red-card rates remain outside the
feature contract.
