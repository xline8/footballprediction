# K-SE-L1 Verdict — Lane 1 re-entry of SE-Allsvenskan cards, arm X8

Date: 2026-11-11. Branch `build/lane1-kse`. Prereg:
`league/SE-Allsvenskan/prereg/PREREG_L1_K_SE.md`, **prereg commit
6e3804f3** (the branch's first commit, before any sealed access).
Dev evaluation commit ce4078c4 (dev-pass token recorded there,
before the sealed read). Run script:
`league/SE-Allsvenskan/engine/cards/run_lane1.py`, executed under
`league/gate_lib/` guards. Original candidate:
`league/SE-Allsvenskan/reports/K_SE_VERDICT.md` (FAIL at the dev
gate — Gate Zero beat neither baseline — sealed window never read).

## Verdict: FAIL — at sealed leg (ii). Nothing ships.

X8 reproduced its documented dev pass exactly and was read once on
the sealed window 2025 (n=240). On that window it **passes leg
(i)** — its LL@3.5 (0.6803) beats Gate Zero's (0.6970) and both
baselines' (base rate 0.7027; naive trailing-10 0.6952) — and
**passes leg (iii)**, the dev sign check, 3/3. But it **fails leg
(ii) outright**: calibration is −4.52pp (predicted − actual),
SE 3.18pp — beyond the 1.0pp tolerance and beyond the 1 SE
provisional boundary (4.18pp). Legs are conjunctive: FAIL, verdict
final, no iteration against the window.

No runner-join change is prepared (join prep is PASS-only), and
the referee operational gate is not run (it gates shipping, and
nothing ships).

## Dev results — reproduced (scored 2022–2024, n=720)

Gate_lib dev evaluation re-ran the league engine on dev data only
(the dev loader's season set excludes 2025 and 2026 in code;
`assert_no_sealed_rows` double-checked). The recomputation
reproduces the original verdict's and the cohort report's numbers
within artefact rounding — the regenerated `results_dev.json` is
byte-identical to the committed artefact:

LL@3.5, pooled dev:

| Arm / baseline | Recomputed | Documented | Reproduced |
|---|---|---|---|
| X8 (arm of record) | 0.6770 (0.6770396) | 0.6770 | yes |
| Gate Zero (baseline only) | 0.6917 (0.6917336) | 0.6917 | yes |
| League base rate | 0.6884 (0.6884278) | 0.6884 | yes |
| Naive trailing-10 | 0.6871 (0.6870554) | 0.6871 | yes |

Dev gate (arm of record beats BOTH baselines): **PASS** —
0.6770 < 0.6884 and 0.6770 < 0.6871. Dev-pass token for `K-SE-L1`
recorded in `engine/cards/lane1_dev_pass_registry.json` before the
sealed read.

Per-season dev LL@3.5 (X8 vs Gate Zero): 2022 0.6940 vs 0.7058;
2023 0.6682 vs 0.6800; 2024 0.6689 vs 0.6894 — sign check
leg (iii): X8 ≤ Gate Zero in **3 of 3** dev seasons, PASS.

Referee coverage in dev (for the record): named referees in
0/240 matches in 2021 (warm-up), 210/240 in 2022, 204/240 in 2023,
170/240 in 2024.

## Sealed results — the single read (2025, n=240)

Loaded once through gate_lib's fail-closed `load_sealed_rows`
(which asserted the recorded dev-pass token first), online
walk-forward continuing from the dev end state. Full numbers in
`engine/cards/results_virgin_lane1.json`; arm-of-record predictions
in `predictions/k_se_lane1_virgin_predictions.csv` (evidence of the
read, not a shipped product).

LL@3.5 on the sealed window:

| Entity | LL@3.5 | Mean P(over 3.5) |
|---|---|---|
| **X8 (arm of record)** | **0.6803** (0.6803145) | 0.4840 |
| Gate Zero (baseline) | 0.6970 (0.6969607) | 0.4893 |
| League base rate | 0.7027 (0.7026697) | — |
| Naive trailing-10 | 0.6952 (0.6952247) | — |

Actual over-3.5 rate on the window: 0.5292 (the dev pooled actual
was 0.4431 — the sealed season's card level ran well above the dev
regime, and every arm under-predicted it; that level miss is what
the failing leg is made of).

| Leg | Result |
|---|---|
| (i) X8 LL ≤ Gate Zero's AND ≤ best baseline's | **PASS** — 0.6803 ≤ 0.6970 (GZ) and ≤ 0.6952 (naive, the best baseline); also ≤ base rate 0.7027 |
| (ii) Calibration \|predicted − actual\| ≤ 1.0pp (clean) / within 1 SE (provisional) | **FAIL** — −4.52pp, SE 3.18pp; provisional boundary is 4.18pp (gate_lib `calibration_band`: FAIL). Gate Zero itself is −3.99pp (SE 3.24pp) — PROVISIONAL band, but Gate Zero cannot ship under this registration and its band does not rescue X8 |
| (iii) Dev sign check ≥ half the dev seasons | PASS — 3/3 |

Referee coverage on the sealed window: 203/240 = 84.6% (matches
the figure published in the original prereg). X8 fallbacks on the
window: 37 unknown-identity, 15 thin-history — those fixtures took
the Gate Zero prediction, per the no-imputation rule.

## P6 worst-fold block

### P6 worst-fold block — SE-Allsvenskan cards (primary metric: ll_3.5)

Source: `league/SE-Allsvenskan/engine/cards/results_dev.json` (persisted dev artefacts; information only — no gate change).
Worst dev season (highest ll_3.5 for the reference arm): **2022**.

| Entity | Pooled ll_3.5 | Pooled source | Worst-season (2022) ll_3.5 | n (worst) | Δ vs pooled |
|---|---|---|---|---|---|
| gate_zero | 0.6917 | n-weighted, computed | 0.7058 | 240 | +0.0141 |
| gate_zero [base] | 0.6884 | n-weighted, computed | 0.6954 | 240 | +0.0070 |
| gate_zero [naive] | 0.6871 | n-weighted, computed | 0.6814 | 240 | -0.0056 |
| x8 | 0.6770 | n-weighted, computed | 0.6940 | 240 | +0.0170 |

Reading (added for this verdict): on the worst dev fold (2022) X8
still beats Gate Zero (0.6940 vs 0.7058) and the base rate
(0.6954), though it loses that fold to naive trailing-10 (0.6814)
— so the pooled dev margin is not uniform across folds. The
sealed failure is nonetheless not a fold artefact: it is the
sealed season's own level rise (actual over-rate 0.5292 vs dev
0.4431), which no dev fold shows at that size.

## Verification notes

- Dev reproduction: byte-identical `results_dev.json`; all four
  pooled numbers within 5e-5 of the documented values.
- Sealed cross-check: the sealed walk-forward was recomputed with
  the league's original harness (`virgin_metrics()`, run in a /tmp
  copy whose persisted dev-gate flag for Gate Zero was flipped
  only there, because that guard is exactly what refuses a
  non-dev-passing comparator) — X8 LL@3.5 0.6803145325686745,
  calibration −0.0452137 (SE 0.0317879), r capped at 500.0 for all
  methods on the full fit, coverage 203/240, fallbacks 37/15:
  identical to this run's gate_lib numbers to every printed digit.
- The original harness's own virgin verdict path cannot be used
  as the gate: `virgin_metrics()` refuses Gate Zero outright (its
  persisted `dev_gate_pass` is false — the §5.6-class trap for
  this J1-seeded family), and `run_k_se.py`'s eligibility merges
  the clean/provisional calibration boundary
  (`|diff| ≤ 0.01 + SE`) instead of the prereg's band. All leg
  arithmetic here is gate_lib's. Note neither divergence changes
  the outcome: even under the harness's merged token, X8's
  |−4.52pp| > 1.0pp + 3.18pp, so calibration fails under either
  reading; leg (i) passes independently.
- The engine's NB r estimates at the capped 500.0 for all methods
  on the sealed walk's full fit (the dev walk's warm-up-only fit
  gave base 75.62 / naive 181.69), exactly as the original harness
  recomputes it — confirmed by the cross-check above, unchanged
  by this entry.
