# Verdict — C-VE

**FAIL.** Gate Zero passes DEV and reads transitional 2026 Clausura, but fails virgin calibration. Nothing ships.

Dev LL@8.5: R1–7 `0.659440`, R8–13 `0.703182`, pooled `0.679629`; base `0.729793`; naive `0.730758` — PASS.

| arm/baseline | virgin LL@8.5 | calibration actual−pred (SE) | legs i/ii |
|---|---:|---:|---|
| Gate Zero | 0.720947 | +9.451pp (5.350) | PASS/FAIL |
| league base | 0.769799 | — | — |
| naive | 0.773869 | — | — |

The breach exceeds 1pp+1SE=6.350pp. Scored n=90, not 91: match 1000018666 has `stats: None` and is not zero-filled. Sensitivity note: the harness league base is the BO/J1-port NB base (LL 0.769799); a literal pooled-rate Bernoulli base at the prior over-rate 0.5000 gives LL 0.6931, which the model (0.7209) also loses to — leg (i) would fail under that definition too. The verdict is unchanged either way: leg (ii) FAIL decides. Transitional season-end confirmatory read remains outstanding. Frozen halves: 0.4669/0.5331.
