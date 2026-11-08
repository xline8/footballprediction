# Verdict — T-AT2 (Austria 2. Liga total shots)

**FAIL — at the virgin calibration leg (all arms). All three arms
passed dev; the virgin window's level collapse kills them.
Nothing ships.**

## Dev (walk-forward; scored 2022/2023–2024/2025, stats n = 708, LL @ 18.5)

| arm | LL @ 18.5 |
|---|---|
| A (v1 pattern) | 0.644618 |
| B (v2 + level layer) | 0.642181 |
| C (E9 trailing-r) | 0.642207 |
| league base rate | 0.664361 |
| naive trailing-10 | 0.699473 |

All three arms beat BOTH baselines — dev gate PASS for A, B, C.

## Virgin (2025/2026, stats n = 210, LL @ 18.5)

| arm | LL @ 18.5 | calibration (actual − pred) | SE |
|---|---|---|---|
| A | 0.642802 | −17.30 pp | 3.02 pp |
| B | 0.627885 | −15.25 pp | 3.02 pp |
| C | 0.627676 | −16.88 pp | 2.99 pp |
| league base rate | 0.799749 | −33.25 pp | |
| naive trailing-10 | 0.641618 | −9.18 pp | |

Leg (i): B (0.627885) and C (0.627676) beat the reference arm A
and the best baseline (naive 0.641618) — PASS; A itself fails leg
(i) against the naive baseline (0.642802 > 0.641618). Leg (ii):
every arm's calibration breach is 15–17 pp against a 1.0 pp
boundary with SE ≈ 3.0 pp — **FAIL**, far beyond provisional
range, for all three arms. Both-pass therefore never engages;
`shipped_arm` is null in `results_virgin.json` and `predictions/`
holds no T-AT2 file, deliberately.

Reading — the F12 caveat, cashed: the models (and even more the
base-rate baseline, −33.25 pp) are priced off dev-era shot levels
that include the contaminated 2024/2025 counting definition
(median 22 shots/match) plus trailing state carried into the
virgin season. The virgin season, counted in the original
definition, delivered a 26.2% over-18.5 rate against predictions
of 41–43%. B and C are genuinely sharp on LL — they beat a naive
baseline that itself missed by −9.18 pp — but a 15 pp
miscalibration at the gated line is not a shippable model. FAIL
is the honest verdict for a candidate whose target series changed
definition mid-window; no era-adjusted rescue arm was registered,
and none may be invented after the read.

Coordinator notes: virgin LLs and calibration diffs recomputed
independently from `engine/total_shots/predictions_virgin.csv`
(210 rows per arm); match the harness to 6dp (SEs cited are the
harness's, per the prereg formula). Dev metrics are taken from
`results_dev.json` — the engine's `predictions_dev.csv` writer
emits header-only output in this engine family (inherited from
the sibling; the scorer's per-season metrics are the dev record,
and the defect is in the secondary writer, not the scorer — its
line substitutions were diff-verified). Two further porting
defects were found and fixed before the virgin run: the virgin
row-count assertion and protocol still carried the sibling's
n=287 (now 210), and the shipped/all predictions writers' field
lists still named the sibling's 14.5/15.5/16.5 lines (now
17.5/18.5/19.5).
