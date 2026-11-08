# Verdict — C-BO (Bolivia Primera Division corners)

**FAIL — both arms fail the dev gate on pooled LL. The 2026 virgin was
NOT read. Nothing ships.**

Prereg: `league/BO-PrimeraDivision/prereg/PREREG_C_BO.md` (frozen
ba94d70, before any fitting). Engine: `engine/corners/` (production
corners_v3 port; Gate Zero carries X9 possession + big-chance
covariates, X7 is the opp-box-touch territorial-multiplier variant).

## Dev gate (pooled, 2025 rounds 11–30 in four expanding 5-round blocks, n=160 scored)

| arm | LL@9.5 |
|---|---|
| Gate Zero | **0.742273** |
| X7 | **0.756243** |
| league base rate | 0.717569 |
| naive trailing-10 | 0.727916 |

Both arms lose to BOTH baselines → **dev gate FAIL** for Gate Zero and
for X7. Per-block Gate Zero LLs: r11-15 0.8519, r16-20 0.7240, r21-25
0.6864, r26-30 0.7068 — the model loses in 3 of 4 blocks and only beats
the base rate in r21-25. X7 is worse than Gate Zero pooled (0.7562 vs
0.7423) and in 3 of 4 blocks. This is not a degenerate fit: both-teams-
active share is 1.0 in every block and the fitted territorial betas are
non-zero (Gate Zero 1.0 in all blocks) — the ratings plus covariates
genuinely do not beat a flat rate on this window. Pooled calibration is
close (predicted over-rate 0.497 vs actual 0.4875) but the per-match LL
is worse, i.e. the model's spread of probabilities is wrong, not its
level.

## Virgin — 2026 regular TRANSITIONAL (n=199 played)

**Not read.** Gate Zero failed dev, so under the frozen rule the virgin
is not read and no arm is evaluated on it. The season-end confirmatory
read is likewise not applicable. Nothing ships.

## Frozen halves constant

Corners 1H share **0.4866** (2025 regular, ratio-of-sums; true variance
≤ 0).
