# Verdict — C-CL (Chile Liga de Primera corners)

**PROVISIONAL PASS — Gate Zero ships.**

## Dev (n = 719, walk-forward 2022–2024, primary line 9.5)

| arm | LL@9.5 |
|---|---|
| Gate Zero | 0.696470 |
| BOXT (X7 box-touch multiplier) | 0.700144 |
| league base rate | 0.737202 |
| naive trailing-10 | 0.732745 |

Both arms beat both baselines → both read the virgin.

## Virgin (2025, n = 240, read once)

| arm | LL@9.5 | calibration (actual − pred) | SE |
|---|---|---|---|
| Gate Zero | 0.694482 | +1.863 pp | 3.236 pp |
| BOXT | 0.694482 | +1.863 pp | 3.236 pp |
| league base rate | 0.735110 | — | — |
| naive trailing-10 | 0.735764 | — | — |

The two arms are **numerically identical on the virgin**: the
virgin-window fit selects beta = 0 for both multipliers
(active-with-nonzero-beta share 0.0), so BOXT collapses to Gate
Zero there. Gate arithmetic: leg (i) 0.694482 ≤ Gate Zero's own
and ≤ best baseline 0.735110 PASS. Leg (ii): |+1.86 pp| breaches
the 1.0 pp boundary, excess 0.86 pp within 1 SE (3.24 pp) →
**PROVISIONAL PASS**. Leg (iii) for BOXT: dev LL ≤ Gate Zero in
2 of 3 seasons (2023, 2024 tied) — passes, but the both-pass tie
on virgin LL goes to the simpler arm → **Gate Zero ships**.

Recorded defect (cosmetic, inherited from the reference harness):
its console line prints the 10.5-line LL/actual under a "9.5"
label; the JSON and CSV outputs are correct and were used here.
All virgin numbers recomputed by the coordinator from the shipped
predictions CSV (exact agreement). Ships: Gate Zero fitted params
+ virgin predictions; 1H/2H presentation via frozen corners
constant 0.4644.
