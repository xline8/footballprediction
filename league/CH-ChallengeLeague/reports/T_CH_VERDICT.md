# Verdict — T-CH (CH-ChallengeLeague total shots): **FAIL (virgin leg ii)**

Frozen decision: PREREG_T_CH.md (prereg commit 157f991, before any fitting).

Dev (2024/2025, n=180; NB r=100): Gate Zero LL @ 26.5 = 0.6826,
beating league base rate (0.6859) and naive trailing-10 (0.7198) —
dev gate PASSED, so the virgin was read once.

Virgin (2025/2026, n=181), primary line 26.5:
- Leg (i) LL: model 0.6757 vs base rate 0.6969, naive trailing-10
  0.7163 → **PASS** (model is the best of the three).
- Leg (ii) calibration: mean P(over 26.5) − actual = −6.37pp,
  SE 3.63pp → the 5.37pp excess beyond the 1.0pp boundary is larger
  than 1 SE → **FAIL** (not provisional).

Diagnosis (recorded, not acted on): total-shots level rose in the
virgin (27.01/match vs dev 25.30); the model ranked matches well
enough to win the LL leg but its probabilities sat systematically
low, which is exactly what the calibration leg exists to catch.
Nothing ships for T-CH.
