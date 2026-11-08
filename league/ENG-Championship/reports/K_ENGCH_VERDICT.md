# Verdict — K-ENGCH (England Championship cards) — **FAIL** (dev gate; virgin NOT read)

Prereg: `prereg/PREREG_K_ENGCH.md`. Primary line 3.5. Gate Zero only
(X8 referee arm dropped in FEATURES: split-half r = 0.259).

## Dev (pooled LL@3.5, n=1,671)

| | LL@3.5 |
|---|---|
| Gate Zero model | 0.6929 |
| League base rate | **0.6880** |
| Naive trailing-10 | 0.6916 |

The model loses to **both** baselines — to the plain league base
rate by 0.0049 LL and even to the naive trailing-10. The dev gate
requires beating both, so Gate Zero is dead at dev. Per the frozen
rule the virgin window (2025/2026) was **deliberately NOT read** and
stays unburned. Nothing ships; no predictions CSV.

The EDA saw this coming and it is recorded plainly: in this league
the team yellows trait itself is **noise** (career split-half
r = −0.01, the weakest target trait in the program) and referee
strictness does not persist either (r = 0.259), so a ratings model
has nothing to grip — Championship card volume is essentially a
league-level rate (≈3.9/match) with match noise on top.
