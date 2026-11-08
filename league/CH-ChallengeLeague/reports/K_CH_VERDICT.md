# Verdict — K-CH (CH-ChallengeLeague cards): **FAIL (dev gate)**

Frozen decision: PREREG_K_CH.md (prereg commit 157f991, before any fitting).
Target: stats-feed total yellows (event feed carries ~no cards in
this league — EDA F5). Virgin 2025/2026 was NOT read for cards.

Dev (2024/2025, n=180, per-match walk-forward; NB r=100):

| Predictor | LL @ 4.5 |
|---|---|
| Gate Zero (trait-rate NB) | 0.6877 |
| League base rate (p=0.522) | 0.6847 |
| Naive trailing-10 | 0.7043 |

Gate Zero beats the naive trailing-10 but loses narrowly to the base
rate (by 0.0030), and the dev gate requires beating both — the arm
is dead at dev. Ladder (context only): LL 3.5 = 0.5568, 5.5 = 0.6777.
Nothing ships for K-CH.
