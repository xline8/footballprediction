# Verdict — S-CH (CH-ChallengeLeague shots on target): **FAIL (dev gate)**

Frozen decision: PREREG_S_CH.md (prereg commit 157f991, before any fitting).
Virgin 2025/2026 was NOT read for SOT.

Dev (2024/2025, n=180, per-match walk-forward; NB r=80):

| Predictor | LL @ 8.5 |
|---|---|
| Gate Zero (trait-rate NB) | 0.7166 |
| League base rate (p=0.517) | 0.6915 |
| Naive trailing-10 | 0.7292 |

The dev gate requires beating BOTH baselines; Gate Zero beats the
naive trailing-10 but loses to the plain base rate, so the arm is
dead at dev. Ladder (context only): LL 7.5 = 0.6326, 9.5 = 0.7012.
Nothing ships for S-CH.
