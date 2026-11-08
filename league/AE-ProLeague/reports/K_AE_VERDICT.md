# Verdict — K-AE (AE-ProLeague cards)

**FAIL at the dev gate. Virgin 2025/2026 deliberately NOT read.**
Nothing ships. Single arm (Gate Zero; X8 dropped pre-fitting —
virgin referee coverage 6/182).

Target: stats-feed yellows (frozen in the prereg with reason: the
event feed carries ~0 plain yellows in 2024/2025 and in the virgin).

Dev LL@3.5 (n=545, recomputed exactly from
`engine/cards/predictions_dev.csv`):

| Kind | LL@3.5 |
|---|---|
| Gate Zero model | **0.708656** |
| League base rate | **0.706214** |
| Naive trailing-10 | 0.708490 |

Gate Zero loses to BOTH baselines pooled (and to the base rate in all
three dev seasons) → dev gate fails. Consistent with the EDA: the
team yellows trait in this league is weak (split-half r=0.318), and at
the 3.5 line the ratings add nothing over the base rate.
