# T-AU verdict — PASS (clean calibration) — arm A (v1 pattern) SHIPS

Prereq: `prereg/PREREG_T_AU.md` (frozen 2026-11-09). Dev gate is pooled LL@27.5 strictly below both baselines. Virgin reference is A; virgin legs are: (i) LL@27.5 no worse than the reference and the best baseline; (ii) calibration within 1.0pp plus one SE, with a breach within one SE provisional; and (iii) variants must beat A in at least 2 of 3 dev seasons.

## Dev

| arm / baseline | pooled LL@27.5 | gate arithmetic |
|---|---:|---|
| A | 0.664950 | < league 0.683610 and < naive 0.666249 — PASS |
| B | 0.662221 | < league 0.683610 and < naive 0.666249 — PASS |
| C | 0.666174 | < league 0.683610 and < naive 0.666249 — PASS |
| league base rate | 0.683610 | baseline |
| naive trailing-10 | 0.666249 | baseline |

All three arms survive the dev gate, so A, B, and C were read once on the 2025/2026 virgin (n=163).

## Virgin

| read arm / baseline | LL@27.5 | calibration (pp) | SE (pp) |
|---|---:|---:|---:|
| A | 0.679763 | -0.65 | 3.87 |
| B | 0.683043 | -1.30 | 3.88 |
| C | 0.679962 | -1.12 | 3.87 |
| league base rate | 0.692891 | +1.25 | 3.91 |
| naive trailing-10 | 0.697554 | +0.51 | 3.93 |

## Gate arithmetic

- A: leg (i) `0.679763 <= 0.679763` and `0.679763 <= 0.692891` — PASS. Leg (ii) `0.65pp <= 1.00 + 3.87pp` — PASS. Reference arm; eligible.
- B: leg (i) `0.683043 <= 0.679763` — FAIL. Leg (ii) `1.30pp <= 1.00 + 3.88pp` — PASS. Dev sign: 2/3 (`2022/2023`, `2023/2024`) — PASS. Not eligible because leg (i) fails.
- C: leg (i) `0.679962 <= 0.679763` — FAIL. Leg (ii) `1.12pp <= 1.00 + 3.87pp` — PASS. Dev sign: 2/3 (`2022/2023`, `2024/2025`) — PASS. Not eligible because leg (i) fails.

**Ships:** arm A (the plain v1 pattern, as in T-J1). Its calibration is clean (−0.65pp ≤ 1.0pp). Arm C (E9) missed leg (i) by 0.0002 LL (0.679962 vs A 0.679763) — effectively tied with A, and the frozen rule gives it to A; fitted parameters in `engine/total_shots/fitted_params_virgin.json`; AU joins the daily runner with total shots (arm A). Coordinator verification: virgin LL@27.5 recomputed from the shipped predictions CSV = 0.679763, matching the results JSON to 6dp; the first harness run scored only A/B on the virgin although C had passed the dev gate (0.666174 < 0.666249 by 0.000075) — caught in verification, C was read, and it fails leg (i) on the numbers above, so the shipped arm is unchanged.

A ships. `predictions/t_au_virgin_predictions.csv` is emitted for A using the frozen AU shots halves constants 0.451/0.549.
