# Verdict — S-SAFD (SA-FirstDivision shots on target) — **CLEAN PASS** (Gate Zero ships)

Prereg: `prereg/PREREG_S_SAFD.md`, frozen 2026-11-10. Target is total
stats-feed SOT; primary line 8.5. Only regular, non-awarded rows were used.
The dev walk-forward used 90 warm-up matches and 214 scored matches,
date-grouped predict-then-update. The 2026/2027 virgin was read once for
both dev-passing arms; it is **TRANSITIONAL** (n=94).

## Dev gate

| Arm | LL@7.5 | LL@8.5 | LL@9.5 | Gate |
|---|---:|---:|---:|---|
| Gate Zero | 0.6587 | 0.6944 | 0.6102 | PASS |
| RS | 0.6598 | 0.6956 | 0.6099 | PASS |
| League base rate | 0.7135 | 0.6963 | 0.6685 | — |
| Naive trailing-10 | 0.6625 | 0.6987 | 0.6119 | — |

At the frozen primary gate, GZ 0.694447 and RS 0.695646 each beat the
league baseline 0.696331 and naive baseline 0.698738.

## Virgin 2026/2027 (TRANSITIONAL, n=94)

| Arm/baseline | LL@8.5 | Calibration (P(over) − actual; SE) |
|---|---:|---:|
| Gate Zero | 0.686013 | −0.686pp (5.145pp) |
| RS | 0.686166 | −0.614pp (5.146pp) |
| League base rate | 0.690133 | — |
| Naive trailing-10 | 0.705866 | — |

Gate arithmetic: leg (i) — GZ 0.686013 ≤ itself and ≤ best baseline
0.690133: PASS. RS 0.686166 ≤ GZ: FAIL, so RS does not ship. RS also
beats the best baseline. Leg (ii) — GZ calibration breach is 0.686pp,
below the 1.000pp limit: CLEAN PASS; RS breach is 0.614pp, also within
the limit. Leg (iii) — GZ is vacuous; RS is not eligible after leg (i).
Both-pass/tie rules are therefore not invoked.

**Ships: Gate Zero.** Predictions are in
`predictions/s_safd_virgin_predictions.csv`; fitted parameters are in
`engine/sot/fitted_params_virgin.json`. Half-time presentation uses the
frozen SOT share 0.4540 / 0.5460 and NB r=79.94; it is not a fitted target.

Verification: dev n=214, virgin n=94, ladder 7.5/8.5/9.5, no X4 arm,
and no 2024/2025 or 2026/2027 rows entered dev fitting.
