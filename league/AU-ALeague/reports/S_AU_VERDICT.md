# S-AU verdict — PASS (calibration PROVISIONAL) — RS (ratio-shrink) SHIPS

Prereq: `prereg/PREREG_S_AU.md` (frozen 2026-11-09). Dev gate is pooled LL@9.5 strictly below both baselines. Virgin legs are: (i) LL@9.5 no worse than GZ and the best baseline; (ii) calibration within 1.0pp plus one SE, with a breach within one SE provisional; and (iii) variants must beat GZ in at least 2 of 3 dev seasons. GZ is exempt from the variant sign leg.

## Dev

| arm / baseline | pooled LL@9.5 | gate arithmetic |
|---|---:|---|
| GZ | 0.685382 | < league 0.696252 and < naive 0.691110 — PASS |
| RS | 0.684044 | < league 0.696252 and < naive 0.691110 — PASS |
| X4 | 0.685314 | < league 0.696252 and < naive 0.691110 — PASS |
| X6 | 0.686221 | < league 0.696252 and < naive 0.691110 — PASS |
| league base rate | 0.696252 | baseline |
| naive trailing-10 | 0.691110 | baseline |

All four arms survive the dev gate, so all four were read once on the 2025/2026 virgin (n=163).

## Virgin

| read arm / baseline | LL@9.5 | calibration (pp) | SE (pp) |
|---|---:|---:|---:|
| GZ | 0.670459 | -1.73 | 3.84 |
| RS | 0.669111 | -1.61 | 3.83 |
| X4 | 0.665528 | -2.46 | 3.82 |
| X6 | 0.660090 | -3.43 | 3.79 |
| league base rate | 0.694482 | — | — |
| naive trailing-10 | 0.680293 | — | — |

## Gate arithmetic

- GZ: leg (i) `0.670459 <= 0.670459` and `0.670459 <= 0.680293` — PASS. Leg (ii) `1.73pp <= 1.00 + 3.84pp` — PASS. GZ is exempt from leg (iii). Eligible.
- RS: leg (i) `0.669111 <= 0.670459` and `0.669111 <= 0.680293` — PASS. Leg (ii) `1.61pp <= 1.00 + 3.83pp` — PASS. Dev sign: 2/3 (`2022/2023`, `2023/2024`) — PASS. Eligible.
- X4: leg (i) `0.665528 <= 0.670459` and `0.665528 <= 0.680293` — PASS. Leg (ii) `2.46pp <= 1.00 + 3.82pp` — PASS. Dev sign: 1/3 — FAIL.
- X6: leg (i) `0.660090 <= 0.670459` and `0.660090 <= 0.680293` — PASS. Leg (ii) `3.43pp <= 1.00 + 3.79pp` — PASS. Dev sign: 1/3 — FAIL.

**Ships:** RS (Gate Zero with the Beta-Binomial ratio prior raised P = 200 → 20,000) — AU's second variant-arm ship of the program (after T-DK arm C), by a margin of 0.0013 LL over Gate Zero. Its calibration breach (−1.61pp) sits within 1 SE (3.83pp) → PROVISIONAL PASS; Gate Zero was also provisional (−1.73pp). X6 posted the best virgin LL of any arm (0.6601) and still cannot ship: its dev sign check is 1/3, applied as written — the same frozen-rule outcome as T-J1 arm C. Fitted parameters in `engine/sot/fitted_params_virgin.json`; AU joins the daily runner with SOT (arm RS). Coordinator verification: virgin LL@9.5 recomputed from the shipped predictions CSV = 0.669111, matching the results JSON to 6dp; the virgin was initially scored for GZ/RS only because the first harness used the sign check as an eligibility filter — caught in verification, repaired, and all four dev-passing arms read before this verdict was written.

RS ships. It is the lower-LL eligible arm than GZ (0.669111 vs 0.670459); X4 and X6 cannot ship because their variant sign leg fails. `predictions/s_au_virgin_predictions.csv` is emitted for RS using the frozen AU halves constants 0.456/0.544.
