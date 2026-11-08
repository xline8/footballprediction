# Verdict — K-RO (RO-LigaI cards, event-unified yellows)

**FAIL — virgin leg (i) (both arms). Nothing ships.**

Dev (pooled n = 945, LL@4.5): Gate Zero 0.6870, X8 0.6878, both
beat league base rate 0.6907 and naive 0.6948 → both arms passed
the dev gate and were read on the virgin window. (X8's dev sign
check vs Gate Zero is 1 of 3, which would have barred it under the
both-pass rule in any case.)

Virgin (2025/2026, n = 315):

| Arm | LL@4.5 | Calibration (pp) |
|---|---|---|
| Gate Zero | 0.6897 | +1.14 (SE 2.81) |
| X8 | 0.6934 | +0.67 (SE 2.82) |
| League base rate | **0.6791** | — |
| Naive trailing-10 | 0.6951 | — |

Gate arithmetic (PREREG_K_RO): leg (i) requires LL ≤ Gate Zero's
AND ≤ the best baseline's. The base rate (0.6791) beats Gate Zero
(0.6897) and X8 (0.6934) → **leg (i) FAILS for both arms**.
Calibration would have been provisional-pass for both (breaches
of 0.14pp / within 1pp against SE ≈ 2.8pp), but leg (i) is
decisive. Referee coverage on the virgin window was ~99.7% — the
X8 failure is a likelihood failure, not a coverage failure
(contrast K-J2). Virgin run reproduces bit-identically on re-run.

Nothing ships.
