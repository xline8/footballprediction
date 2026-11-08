# T-J1 Verdict — J1 total shots model

Date: 2026-11-09. Branch `build/t-j1`. Prereg:
`league/J1/prereg/PREREG_T_J1.md` (committed a759c32, before any
fitting). Engine: `league/J1/engine/total_shots/`, implemented by
Codex (gpt-5.6-luna) from the coordinator's brief, then verified
independently by the coordinator (below). Production untouched;
the top-5 prospective trial (v2 + E9) untouched.

## Frozen setup (from the prereg)

- Target: total shots (stats feed), J1 only. Primary line
  **24.5** (dev 2022–2025 mean 24.898, median 24.0; over-rate at
  24.5 = 48.69%, closest to 50%). Ladder 23.5/24.5/25.5.
- Tuning (season 2022 only): ridge lambda = **100** (grid LL@24.5:
  3→0.6615, 10→0.6597, 30→0.6572, 100→0.6542, 300→0.6558);
  r_A = **114.72** (method of moments, 2021–2022 residuals);
  arm B level cell = **HL 120 d, s 0.5, K 50** (best of the 12
  frozen cells on 2022, LL 0.6609).
- Dev gate pool: seasons 2023–2025 (n = 1,066). Virgin: season
  "2026" (n = 200), read once, dev-passing arms only.

## Dev results — pooled LL@24.5 (gate pool 2023–2025)

| Method | LL@23.5 | LL@24.5 | LL@25.5 | Calib @24.5 | MAE |
|---|---|---|---|---|---|
| Arm A (v1 pattern) | 0.6538 | **0.6548** | 0.6458 | +0.30pp | 4.372 |
| Arm B (+ level layer) | 0.6538 | 0.6551 | 0.6462 | +0.92pp | 4.374 |
| Arm C (E9 trailing-r) | 0.6538 | 0.6549 | 0.6461 | +0.20pp | 4.372 |
| Baseline (a) league base rate | 0.6846 | 0.6925 | 0.6826 | +1.07pp | 4.601 |
| Baseline (b) naive trailing-10 | 0.6658 | 0.6648 | 0.6544 | +2.59pp | 4.412 |

Dev gate — pooled dev LL@24.5 beats BOTH baselines: **A pass,
B pass, C pass.** All three arms were read on the virgin window.

Per-season LL@24.5 (for leg iii):

| Season | A | B | C |
|---|---|---|---|
| 2023 | 0.6553 | 0.6560 | 0.6559 |
| 2024 | 0.6481 | 0.6481 | 0.6486 |
| 2025 | 0.6612 | 0.6614 | 0.6603 |

## Virgin results — season "2026" (n = 200, read once)

Actual over-rate @24.5: 53.0%.

| Method | LL@23.5 | LL@24.5 | LL@25.5 | Calib @24.5 | SE | MAE |
|---|---|---|---|---|---|---|
| Arm A | 0.6766 | **0.691571** | 0.6699 | −2.30pp | 3.52pp | 4.357 |
| Arm B | 0.6777 | 0.692858 | 0.6703 | −2.23pp | 3.53pp | 4.367 |
| Arm C | 0.6761 | 0.691230 | 0.6698 | −2.45pp | 3.52pp | 4.357 |
| Baseline (a) league | 0.6799 | 0.692827 | 0.6864 | −1.41pp | 3.53pp | 4.430 |
| Baseline (b) naive | 0.7014 | 0.718960 | 0.6882 | −1.92pp | 3.61pp | 4.445 |

## Gate legs (prereg, verbatim) applied mechanically

- **Leg (i)** — virgin LL@24.5 ≤ reference (arm A, which passed
  dev: 0.691571) and ≤ best baseline (league, 0.692827):
  A **PASS** (0.691571 ≤ both); B **FAIL** (0.692858 is worse
  than arm A and worse than the league baseline); C **PASS**
  (0.691230 ≤ both).
- **Leg (ii)** — calibration |mean P(over 24.5) − actual| ≤
  1.0pp, breach within 1 SE = PROVISIONAL PASS: A −2.30pp,
  breach 1.30pp ≤ SE 3.52pp → **PROVISIONAL PASS**; B −2.23pp →
  PROVISIONAL (moot, B already fails leg i); C −2.45pp, breach
  1.45pp ≤ SE 3.52pp → **PROVISIONAL PASS**. The SE is large
  because n = 200 (sd(p−y) ≈ 0.49); no arm point-passes this
  leg, and the provisional status is part of the verdict, not a
  footnote.
- **Leg (iii)** — dev per-season sign check vs arm A (≥ 2 of 3
  seasons with LL ≤ A's): B wins only 2024 (0.648072 vs
  0.648138) → **1/3, FAIL**; C wins only 2025 → **1/3, FAIL**.

## Verdict per arm

- **Arm A (v1 pattern): PASS** (dev gate ✓, leg i ✓, leg ii
  PROVISIONAL PASS). Ships.
- **Arm B (v2 level layer): FAIL** — legs (i) and (iii). On J1
  the level layer added nothing: dev LL slightly worse than A,
  virgin LL worse than the plain league base rate.
- **Arm C (E9 trailing-r): FAIL** — leg (iii), despite the best
  virgin LL of the three arms (0.691230). The prereg's sign
  check is a pass condition for variant arms, fixed before
  fitting; it is not waived after the fact. The trailing-r
  mechanism's J1 dev record (better than A in only 1 of 3
  seasons, pooled dev LL a hair worse) does not support
  shipping it over the reference arm.

**T-J1: PASS — arm A ships**, with its calibration leg recorded
as PROVISIONAL PASS. Predictions:
`league/J1/predictions/t_j1_virgin_predictions.csv` (arm A, 200
rows, FT ladder + 1H/2H ladders via the frozen 0.455 constant,
presentation only). The reserved confirmatory virgin window
(2026/2027, per the shared frame) is the natural place for the
provisional calibration to be confirmed or revoked; it is not
read here.

## Context (readings, not verdicts)

Against the family's top-5 history: v1's candidate was the
sharpest predictor in its test window but failed calibration at
−1.34pp pooled; v2's level-layer design then failed its virgin
window outright at −6.04pp calibration in an extreme
early-season shot regime. The J1 readings rhyme with that
history in miniature: on the virgin 2026 window every arm —
and both baselines — under-predicted the over-rate (actual
53.0% vs predictions near 51%), the level layer again failed
to beat its own base arm, and the trailing-r variant again
showed the best single-window log loss without the consistent
per-season dev record the gate asks for. The magnitudes here
are far milder than the top-5 v2 failure and the J1 window is
small (n = 200, calibration SE 3.5pp), so these are readings to
carry into the confirmatory window, not conclusions about the
top-5 trial, which remains frozen and untouched.

## Coordinator verification (independent of the implementer)

- Re-ran `dev` and `virgin --export-arm A` end to end: all
  metrics reproduce the implementer's to ≤ 9e-8 (BLAS-level
  floating noise); every gate margin is at least 3e-5, so no
  decision is within noise of flipping.
- Virgin isolation: the dev step loads seasons 2021–2025 only
  (count-asserted 380/306/306/380/380, explicit assert that no
  2026 row is present); the virgin step is a separate run that
  refuses to export an arm whose recorded `dev_pass` is not
  true.
- Arm C causality: `TrailingR.value(day)` recomputed
  independently from the raw CSV at 13 sampled matches (last
  200 totals with date strictly before the match date) — exact
  agreement, max difference 0.0.
- Five virgin predictions checked by hand from the exported
  CSV: FT/1H/2H totals split exactly by 0.455/0.545, halves NB
  probabilities recomputed with an independent implementation
  match exactly, and arm A's virgin LL@24.5 and calibration
  recomputed from the CSV columns alone reproduce
  `results_virgin.json` to all printed digits.
- Two implementer deviations were caught in review and fixed
  before any number was accepted: (1) ensemble probabilities
  were first computed as the NB probability of the averaged
  total instead of the prereg's average of the two members' NB
  probabilities; (2) arm C's trailing window first absorbed
  same-day matches instead of the prereg's strictly-prior-date
  release. Both fixes are in the committed engine; all numbers
  above are from the fixed code.
- The implementer could not commit from its sandbox (git
  metadata read-only there); all commits on `build/t-j1` were
  made by the coordinator after verification.
