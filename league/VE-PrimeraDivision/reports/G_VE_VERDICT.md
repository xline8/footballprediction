# Verdict — G-VE

**FAIL.** Both dev-passing arms were read on 2025 regular (n=182); both fail virgin home-win calibration. Nothing ships.

Dev (model vs climatology): Gate Zero `1.072023 / 0.218352 / 0.675617` vs `1.079346 / 0.220976 / 0.686472`; SHRINK is identical. Both pass all dev legs. SHRINK's sign check is 2/2; the tie rule favors Gate Zero.

| arm | virgin 1X2 LL | RPS | OU2.5 LL | home cal actual−pred (SE) | OU2.5 cal actual−pred (SE) | legs i/ii/iii |
|---|---:|---:|---:|---:|---:|---|
| Gate Zero | 0.987082 | 0.205635 | 0.693311 | +8.221pp (3.513) | +3.145pp (3.702) | PASS/FAIL/PASS |
| SHRINK | 0.987082 | 0.205635 | 0.693311 | +8.221pp (3.513) | +3.145pp (3.702) | PASS/FAIL/PASS |
| climatology | 1.059978 | — | 0.685032 | — | — | — |

The home breach exceeds 1pp+1SE=4.513pp; OU2.5 is only provisional. Independent CSV recomputation gives climatology OU2.5 LL 0.685032. Frozen halves: 0.4478/0.5522.
