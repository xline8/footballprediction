# Verdict — K-MA (Morocco Botola Pro cards)

**FAIL at the dev gate. Virgin NOT read. Nothing ships.**

Prereg: `prereg/PREREG_K_MA.md`. Target: event-unified yellows
(Yellow + YellowRed), rich era only — the stats feed has no cards
key at all, so no stats target exists (artefact check moot,
recorded in the prereg before fitting). Dev = rich-era scored
window 2025-01-01 – 2025-05-12, n=112. Arm numbers recomputed by
the coordinator from `engine/cards/predictions_dev.csv` and match
`results_dev.json`.

## Dev LL @ 4.5 (pooled, n=112)

| arm / baseline | LL@4.5 | mean P(over 4.5) |
|---|---|---|
| Gate Zero (cards pattern) | 0.6928 | 0.4658 |
| league base rate | 0.6936 | 0.4696 |
| naive trailing-10 | **0.6724** | 0.4543 |

Actual over-rate 0.4464; actual mean total 4.26 vs model mean
4.58.

Dev gate (verbatim): pooled dev LL@4.5 must beat BOTH baselines.
Gate Zero beats the league base rate by 0.0008 but loses clearly
to naive trailing-10 (0.6928 > 0.6724) → dev gate FAILS. The
virgin (2025/2026) is NOT read; K-MA is FAIL.

This is consistent with the EDA warning recorded before fitting:
team yellows-for split-half reliability in the rich dev era is
r = 0.010 (noise), so a ratings-based cards model had little team
signal to work with, and the simple trailing-10 mean of the
target itself was the stronger predictor on this window.

No fitted params ship, no predictions. Production code untouched.
