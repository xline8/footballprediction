# Verdict — K-BO (Bolivia Primera Division cards)

**FAIL — Gate Zero beats the league base rate but loses to the naive
trailing-10 baseline on pooled dev LL. The 2026 virgin was NOT read.
Nothing ships.**

Prereg: `league/BO-PrimeraDivision/prereg/PREREG_K_BO.md` (frozen
ba94d70, before any fitting). Engine: `engine/cards/` (Gate Zero only;
X8 dropped — referee named on 40/240 matches in 2025). Target is
**event-unified yellows** (Yellow + YellowRed events), not the stats-feed
yellow columns, which undercount 1,324 vs 1,495 in 2025.

## Dev gate (pooled, 2025 rounds 11–30 in four expanding 5-round blocks, n=160 scored)

| arm | LL@6.5 |
|---|---|
| Gate Zero | **0.662719** |
| league base rate | 0.695092 |
| naive trailing-10 | 0.654949 |

Gate Zero beats the base rate by 0.032 but loses to the naive baseline
by 0.008 → **dev gate FAIL** (the gate requires beating both).
Per-block model LLs: r11-15 0.7054, r16-20 0.6782, r21-25 0.6431,
r26-30 0.6242 — the model improves block by block but never catches the
naive pooled. NB dispersion r is capped at 500.0 for all three methods:
the seed window is underdispersed (mean 6.39, variance 5.11), so the
moment estimator's denominator is negative and the cap makes the model
effectively Poisson. That is the estimator's honest output on this
window, not a bug — but it means the NB layer adds nothing here.

## Virgin — 2026 regular TRANSITIONAL (n=199 played)

**Not read.** Gate Zero failed dev, so under the frozen rule the virgin
is not read. The season-end confirmatory read is likewise not
applicable. Nothing ships.

## Frozen halves constant

Yellows 1H share **0.3739** (2025 regular, event-unified, ratio-of-sums;
a +0.004 single-season residual in the variance decomposition is
flagged for recheck when a second stats season exists).
