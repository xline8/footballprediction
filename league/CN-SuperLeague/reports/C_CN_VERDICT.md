# Verdict — C-CN (corners): **FAIL**

Prereg: `prereg/PREREG_C_CN.md` (frozen and committed before fitting).
Primary line 9.5. Era 2023+; dev scored 2024+2025 (n = 480); virgin
2026 (n = 240). All numbers recomputed by the coordinator from the
per-match prediction CSVs against the league CSV.

Coordinator correction during the build: the copied TH core had
silently replaced the trailing territorial big-chance differential
(z_bc) with the target match's OWN big_chance split (same-match
leakage). Restored to the J1 original before any CN fitting; the dev
and virgin numbers below are from the corrected engine.

## Dev (per-season fits on prior seasons only)

| Arm | Pooled LL@9.5 | 2024 | 2025 |
|---|---|---|---|
| Gate Zero | 0.6961 | 0.6877 | 0.7045 |
| X7 (box touches) | 0.7395 | 0.7782 | 0.7009 |
| League base rate | 0.7622 | — | — |
| Naive trailing-10 | 0.7450 | — | — |

Dev gate: both arms beat both baselines → both read on the virgin.
(X7's dev edge is thin and driven by 2025; its fitted beta_bt for the
2025 fit was 0.0.)

## Virgin (2026, read once)

| Arm | LL@9.5 | Mean pred P(over) | Actual over-rate | Calibration (pp) | SE (pp) |
|---|---|---|---|---|---|
| Gate Zero | 0.7063 | 0.5480 | 0.4833 | −6.47 | 3.25 |
| X7 | 0.7012 | 0.5470 | 0.4833 | −6.37 | 3.23 |
| League base rate | 0.7140 | — | — | — | — |
| Naive trailing-10 | 0.7160 | — | — | — | — |

## Gate arithmetic

- Leg (i) LL: both arms beat the best baseline (0.7063 / 0.7012 <
  0.7140) ✓.
- Leg (ii) calibration: Gate Zero breach −6.47pp, X7 −6.37pp. The
  provisional boundary is 1.0pp + 1 SE ≈ 4.25pp; both breaches are
  beyond it → **leg (ii) FAIL for both arms**. The 2026 corner level
  fell back (9.99/match vs dev-era 10.27 and 10.49 in 2024) while the
  season-blocked fits, trained on the high 2024–2025 window, kept
  predicting the higher level: mean predicted over-rate 0.548 against
  an actual 0.483.

Both arms fail leg (ii) → **C-CN FAILS. Nothing ships.**
