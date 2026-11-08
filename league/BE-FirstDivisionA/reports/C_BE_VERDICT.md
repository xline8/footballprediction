# C-BE verdict — FAIL

Prereg: `prereg/PREREG_C_BE.md` (frozen f0c214a, before fitting).
Primary line **9.5** (dev over-rate 0.533). Dev pooled n = 955
(score-only match excluded — target absent); virgin 2025/2026
n = 313, read once, for both dev-passing arms.

## Dev results — pooled LL@9.5

| Arm / baseline | LL@9.5 |
|---|---|
| Gate Zero (X9) | 0.6931 |
| X7 (box touches) | 0.6931 |
| League base rate | 0.7284 |
| Naive trailing-10 | 0.7303 |

Both arms beat both baselines by a wide margin → both pass the
dev gate.

## Virgin results (2025/2026, n = 313)

| Arm / baseline | LL@9.5 | Calibration (mean P − actual) |
|---|---|---|
| Gate Zero | 0.6815 | −4.34pp (SE 2.79pp) |
| X7 | 0.6815 | −4.34pp (SE 2.79pp) |
| League base rate | 0.7586 | — |
| Naive trailing-10 | 0.7517 | — |

## Gate arithmetic

- Leg (i): both arms pass easily (0.6815 ≤ best baseline 0.7517).
- Leg (ii): **both arms FAIL.** |−4.34pp| breaches the 1.0pp
  boundary by 3.34pp, beyond 1 SE (2.79pp). The virgin season's
  corner volume at the 9.5 line ran far above prediction (actual
  over-rate 56.9% vs mean predicted 52.5%) even though the season's
  corner *mean* (10.16) was unremarkable — the over-rate at this
  line, not the level, is what moved.
- Leg (iii): X7's dev predictions are identical to Gate Zero's, so
  the sign check is 3/3 by equality — moot under leg (ii).

The two arms' virgin predictions are **identical** — on the virgin
fit both territorial betas fitted to exactly 0.0 (γ = 0.15,
r = 1.1194 for both), the same result C-J1, C-DK and C-CH recorded:
the box-touch trait is real in BE too (split-half r = 0.916/0.824)
but earns exactly zero inside this multiplier structure.

**Verdict: FAIL. Nothing ships.** (The harness's per-arm
`fitted_params_virgin.json` was removed on FAIL; the fitted values
remain recorded in `results_virgin.json`.) The dev margin was the
largest of any BE candidate and the candidate still dies on virgin
calibration — a level-shift failure, not a ranking failure.
