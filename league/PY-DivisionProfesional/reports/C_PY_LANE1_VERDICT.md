# C-PY-L1 Verdict — Lane 1 re-entry of PY-DivisionProfesional corners, arm X7

Date: 2026-11-11. Branch `build/lane1-cpy`. Prereg:
`league/PY-DivisionProfesional/prereg/PREREG_L1_C_PY.md`,
**prereg commit 40ab323a** (the branch's first commit, before any
sealed access). Dev evaluation commit 97b020c8 (dev-pass token
recorded there, before the sealed read). Run script:
`league/PY-DivisionProfesional/engine/corners/run_lane1.py`,
executed under `league/gate_lib/` guards. Original candidate:
`league/PY-DivisionProfesional/reports/C_PY_VERDICT.md` (FAIL at
the dev gate — Gate Zero lost to naive trailing-10 — sealed window
never read).

## Verdict: FAIL — at sealed legs (i) and (ii). Nothing ships.

X7 reproduced its documented dev pass exactly and was read once on
the frozen sealed cohort, 2026 - Clausura (n = 112). On that window
it beats both baselines but **loses leg (i) to Gate Zero** — X7
LL@8.5 0.6973 vs Gate Zero 0.6927 — and **fails leg (ii)
outright**: calibration is −7.80pp (predicted − actual), SE
4.70pp — beyond the 1.0pp tolerance and beyond the 1 SE
provisional boundary (5.70pp). Leg (iii), the dev sign check,
passes 2/2. Legs are conjunctive: FAIL, verdict final, no
iteration against the window.

No runner-join change is prepared (join prep is PASS-only).

## Frozen-cohort note (per the prereg)

The window was TRANSITIONAL at the original pull and the original
prereg froze it at **n = 112** (played 2026-07-24 to 2026-11-08).
The league data snapshot used for this read contains exactly 112
rows for 2026 - Clausura — the frozen n — so the read used exactly
the prereg's frozen definition and cohort. No widening occurred
and none was needed; had the data contained more window matches,
only the frozen cohort would have been read.

## Dev results — reproduced (seed 2025-Ap; scored 2025-Cl + 2026-Ap, n = 263)

Gate_lib dev evaluation re-ran the league engine on dev data only
(the dev loader's season set excludes 2026 - Clausura in code;
`assert_no_sealed_rows` double-checked). The recomputation
reproduces the original verdict's and the cohort report's numbers
exactly — every pooled value matches the committed
`results_dev.json` artefact to the last printed digit:

LL@8.5, pooled dev:

| Arm / baseline | Recomputed | Documented | Reproduced |
|---|---|---|---|
| X7 (arm of record) | 0.6918 (0.6917816) | 0.6918 | yes |
| Gate Zero (baseline only) | 0.7211 (0.7210736) | 0.7211 | yes |
| League base rate | 0.7313 (0.7312518) | 0.7313 | yes |
| Naive trailing-10 | 0.7180 (0.7180172) | 0.7180 | yes |

Dev gate (arm of record beats BOTH baselines): **PASS** —
0.6918 < 0.7313 and 0.6918 < 0.7180. Dev-pass token for `C-PY-L1`
recorded in `engine/corners/lane1_dev_pass_registry.json` before
the sealed read.

Per-block dev LL@8.5 (X7 vs Gate Zero): 2025-Cl 0.6965 vs 0.7523;
2026-Ap 0.6870 vs 0.6896 — sign check leg (iii): X7 ≤ Gate Zero
in **2 of 2** dev blocks, PASS.

## Sealed results — the single read (2026 - Clausura, frozen n = 112)

Loaded once through gate_lib's fail-closed `load_sealed_rows`
(which asserted the recorded dev-pass token first); the sealed fit
is the original harness's virgin construction (parameters fitted
on all non-virgin rows, fit_n = 385; gamma 0.3, r 1.2278 for both
arms; Gate Zero beta [0.0025, 0.0], X7 beta [0.01]). Full numbers
in `engine/corners/results_virgin_lane1.json`; arm-of-record
predictions in `predictions/c_py_lane1_virgin_predictions.csv`
(evidence of the read, not a shipped product).

LL@8.5 on the sealed window:

| Entity | LL@8.5 | Mean P(over 8.5) |
|---|---|---|
| Gate Zero (baseline) | **0.6927** (0.6926573) | 0.5429 |
| **X7 (arm of record)** | **0.6973** (0.6972663) | 0.5470 |
| Naive trailing-10 | 0.7695 (0.7695031) | 0.4093 |
| League base rate | 0.7990 (0.7989612) | 0.3661 |

Actual over-8.5 rate on the window: 0.6250 (the dev pooled actual
was 0.4905 — the sealed tournament's corner level ran far above
the dev regime, and every arm under-predicted it; that level miss
is what the failing calibration leg is made of, and on LL the
touches multiplier, fitted at its grid maximum beta 0.01 on the
dev-era fit, slightly hurt rather than helped).

| Leg | Result |
|---|---|
| (i) X7 LL ≤ Gate Zero's AND ≤ both baselines' | **FAIL** — 0.6973 > 0.6927 (Gate Zero); X7 does beat naive (0.7695) and the base rate (0.7990), but the leg is conjunctive |
| (ii) Calibration \|predicted − actual\| ≤ 1.0pp (clean) / within 1 SE (provisional) | **FAIL** — −7.80pp, SE 4.70pp; provisional boundary is 5.70pp (gate_lib `calibration_band`: FAIL). Gate Zero itself is −8.21pp (SE 4.68pp) — also FAIL band |
| (iii) Dev sign check ≥ half the dev blocks | PASS — 2/2 |

## P6 worst-fold block

### P6 worst-fold block — PY-DivisionProfesional corners (primary metric: ll_8.5)

Source: `league/PY-DivisionProfesional/engine/corners/results_dev.json` (persisted dev artefacts; information only — no gate change).
Worst dev season (highest ll_8.5 for the reference arm): **2025 - Clausura**.

| Entity | Pooled ll_8.5 | Pooled source | Worst-season (2025 - Clausura) ll_8.5 | n (worst) | Δ vs pooled |
|---|---|---|---|---|---|
| gate_zero | 0.7211 | n-weighted, computed | 0.7523 | 132 | +0.0313 |
| league_base_rate | 0.7313 | n-weighted, computed | 0.7650 | 132 | +0.0338 |
| naive_trailing_10 | 0.7180 | n-weighted, computed | 0.7310 | 132 | +0.0130 |
| x7 | 0.6918 | n-weighted, computed | 0.6965 | 132 | +0.0047 |

Reading (added for this verdict): on the worst dev fold
(2025 - Clausura) X7 still beats Gate Zero (0.6965 vs 0.7523) and
both baselines — its pooled dev margin is not a one-fold artefact,
and its worst fold is the most stable of the four entities
(Δ +0.0047). The sealed failure is the sealed tournament's own
level rise (actual over-rate 0.6250 vs dev 0.4905), which no dev
fold shows, compounded by the touches multiplier adding a small
LL cost on the window instead of the gain it gave on dev.

## Verification notes

- Dev reproduction: exact — all four pooled numbers match the
  committed `results_dev.json` artefact to the last printed digit.
- Sealed cross-check: the sealed construction was recomputed with
  the league's original harness (`harness.virgin()`, run in a /tmp
  copy whose `gate_passes` guard was monkeypatched there only,
  because that guard is exactly what refuses the non-dev-passing
  Gate Zero comparator) — Gate Zero LL@8.5 0.6926573450243775,
  X7 LL@8.5 0.697266316884132, calibration −8.21pp / −7.80pp with
  SEs 4.68pp / 4.70pp, baselines 0.7989612 / 0.7695031: identical
  to this run's gate_lib numbers to every printed digit.
- The original harness's own virgin verdict path cannot be used
  as the gate: `run_c_py.py` refuses the whole read when Gate
  Zero fails its dev gate (the frozen rule this Lane 1 entry
  exists to supersede for the arm of record), and its calibration
  token merges the clean/provisional boundary
  (`|diff| ≤ 0.01 + SE`, the §5.6 class) instead of the prereg's
  band. All leg arithmetic here is gate_lib's. Note neither
  divergence changes the outcome: even under the harness's merged
  token, X7's |−7.80pp| > 1.0pp + 4.70pp, so calibration fails
  under either reading, and leg (i) fails independently.
