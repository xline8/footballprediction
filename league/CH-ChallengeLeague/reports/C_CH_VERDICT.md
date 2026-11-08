# Verdict — C-CH (CH-ChallengeLeague corners): **FAIL (virgin legs i + ii)**

Frozen decision: PREREG_C_CH.md (prereg commit 157f991, before any fitting).

Dev (2024/2025, n=180; NB r=21): Gate Zero LL @ 8.5 = 0.6866, beating
naive trailing-10 (0.7027) and league base rate (0.7406) — dev gate
PASSED, so the virgin was read once.

Virgin (2025/2026, n=181), primary line 8.5:
- Leg (i) LL: model 0.7144 vs base rate 0.6897, naive trailing-10
  0.7203 → **FAIL** (must be ≤ best baseline; the base rate wins).
- Leg (ii) calibration: mean P(over 8.5) − actual = −6.97pp,
  SE 3.77pp → breach beyond 1 SE of the 1.0pp boundary → **FAIL**.

Diagnosis (recorded, not acted on): the corners level rebounded in
the virgin (8.87/match after the dev season's 8.49, warm-up 9.99);
the trait model, anchored on the low dev level, under-predicted
throughout. Nothing ships for C-CH.
