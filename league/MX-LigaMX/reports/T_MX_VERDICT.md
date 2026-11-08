# T-MX Verdict — Liga MX total-shots model

Date: 2026-11-09. Branch `build/mx-ligamx`. Prereg:
`league/MX-LigaMX/prereg/PREREG_T_MX.md` (commit 8512c8d, frozen
before any fitting). Engine:
`league/MX-LigaMX/engine/total_shots/`. Implementation by Codex
(gpt-5.6-luna) under the two-agent flow; the coordinator
independently re-ran the dev harness and reproduced every number
(see Verification notes). Predictions-only product: no Liga MX
total-shots odds source exists in-system — expected, not a
defect.

## Verdict: FAIL — all arms fail the virgin gate; nothing ships

All three arms pass the dev gate comfortably and are read on the
virgin. The virgin block ran hot on shots (actual over-rate at
26.5 = 56.2% against a dev 49.4%) and every arm under-predicts it
by ~6.2pp — beyond the 1 SE provisional band — so the calibration
leg fails for all three. Every arm also loses virgin LL to the
naive trailing-10 (0.6601), failing leg (i) independently. Arm B
additionally arrives at the virgin already ineligible under the
prereg's sign-check leg (3/8). Nothing ships. Arm A's virgin
predictions file exists as the harness's fallback export, labelled
as such here — it is **not** a shipped product.

## Dev results (per-match walk-forward, scored blocks = tournaments 2–9, n = 1,224; LL@26.5)

Pooled (tuned on dev only, per the frozen protocol: ridge λ over
{3, 10, 30, 100, 300} → 300; NB r ≈ 77.46; level cell
(120, 0.5, 50); M_BAR = 26.65):

| Arm | LL@26.5 | Calibration | vs base 0.6936 | vs naive 0.6795 |
|---|---|---|---|---|
| A (separate attack/defence) | 0.6725 | −0.09pp (SE 1.40) | pass | pass |
| B (interaction cell) | 0.6727 | +0.47pp | pass | pass |
| C (single total rating) | 0.6724 | +0.06pp | pass | pass |
| League base rate | 0.6936 | — | — | — |
| Naive trailing-10 | 0.6795 | — | — | — |

Per-block LL@26.5:

| Block | A | B | C | Base | Naive |
|---|---|---|---|---|---|
| 2021/2022 - Clausura | 0.6528 | 0.6545 | 0.6528 | 0.6768 | 0.6605 |
| 2022/2023 - Apertura | 0.6623 | 0.6614 | 0.6623 | 0.7019 | 0.6670 |
| 2022/2023 - Clausura | 0.6796 | 0.6750 | 0.6794 | 0.6880 | 0.6893 |
| 2023/2024 - Apertura | 0.6792 | 0.6816 | 0.6795 | 0.6927 | 0.7006 |
| 2023/2024 - Clausura | 0.6791 | 0.6802 | 0.6792 | 0.6941 | 0.6837 |
| 2024/2025 - Apertura | 0.6701 | 0.6701 | 0.6689 | 0.6977 | 0.6756 |
| 2024/2025 - Clausura | 0.6777 | 0.6778 | 0.6782 | 0.7029 | 0.6842 |
| 2025/2026 - Apertura | 0.6790 | 0.6808 | 0.6791 | 0.6943 | 0.6753 |

Sign check (variant dev LL ≤ A, of 8): B 3/8 (**fails leg iii**),
C 4/8 (passes).

## Virgin results (2025/2026 - Clausura, n = 153, read once)

| Arm | LL@26.5 | Mean P(over) | Actual over | Calibration diff | SE |
|---|---|---|---|---|---|
| A | 0.6777 | 49.99% | 56.21% | −6.22pp | 3.95pp |
| B | 0.6768 | 50.21% | 56.21% | −6.00pp | 3.95pp |
| C | 0.6778 | 49.99% | 56.21% | −6.22pp | 3.95pp |
| League base rate | 0.6931 | 49.63% | 56.21% | −6.58pp | 4.01pp |
| Naive trailing-10 | **0.6601** | 52.34% | 56.21% | −3.87pp | 3.90pp |

## Gate arithmetic

- Dev gate (pooled LL@26.5 beats both baselines + dev calibration
  within the provisional band): A, B, C all **pass**.
- Virgin leg (i) (LL ≤ A's LL AND ≤ best baseline's): A — 0.6777
  ≤ 0.6777 but > naive 0.6601 → **FAIL**. B — 0.6768 ≤ A but >
  0.6601 → **FAIL**. C — 0.6778 > A and > 0.6601 → **FAIL**.
- Virgin leg (ii) (calibration): all arms |diff| ≈ 6.0–6.2pp >
  1.0pp + 1 SE (≈4.95pp) → **FAIL** for every arm. Notably even
  the league base rate under-predicts by 6.58pp: the block was
  simply shot-heavy (mean total 27.92 vs dev 26.65), and only the
  fast-adapting naive stayed within reach.
- Virgin leg (iii): B 3/8 < 4 → **ineligible regardless**; C 4/8
  passes, moot given legs (i)/(ii).
- No arm passes → **T-MX is FAIL; nothing ships.**

Recorded plainly: this is the top-5 v2 failure shape transplanted
— a level shift in the virgin window that slow level-anchored
ratings cannot follow within one 153-match block. The dev record
(all arms within 0.0003 of each other, calibration ±0.5pp) says
the machinery is sound in-regime; the frozen virgin says it does
not survive this regime change. No recalibration rescue is
attempted — the prospective-trial discipline in the prereg
applies to this market family, and any retry needs a new prereg
and a new virgin.

## Verification notes (coordinator, independent of Codex)

- Coordinator review fixed AR-port leftovers before the read
  (predictions filename `t_ar_…` → `t_mx_…`; a dead AR season
  check in the loader). The virgin label, block counts (9 dev
  blocks, 153 virgin matches) and halves constants (0.458/0.542)
  were already correct in the port and are confirmed in the
  results file's protocol block.
- Coordinator re-run of the dev harness reproduces every pooled
  and per-block number (agreement to ~1e-8 on the fitted r from
  floating-point summation order; all gate-relevant figures
  identical at 4 dp), including the dev-pass flags (A/B/C true)
  and the tuned λ = 300, level cell (120, 0.5, 50).
- All three arms were read on the virgin exactly as the dev gate
  allowed; B's leg (iii) ineligibility is recorded from the dev
  sign check, not from its virgin LL (which was, incidentally,
  the lowest of the three — the frozen rule still bars it).
- Fallback export: `predictions/t_mx_virgin_predictions.csv`
  (153 rows, arm A) and `engine/total_shots/fitted_params_virgin.json`
  retained as the record of the read, not a ship.
