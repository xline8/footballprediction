# Halves experiment 3: constant-share goal halves under a production-faithful refit harness

Date: 2026-11-08. Script: `run_halves_goals_v3.py`. Artifacts:
`halves_v3_aggregates.json`, `halves_v3_test_permatch.csv`.
Follow-up to experiment 2 (`RESULTS_HALVES_GOALS_V2.md`, GATE FAIL),
whose measured diagnosis was that the verdict might be a harness
artefact: V2's FT lambdas came from a static goals-only fit (train
≤2022/23) while production refits weekly. The user ordered the cause
fixed ("saya mau model gol first half dan second half nya lolos");
the gate below was NOT moved.

## Gate (pre-registered, identical to V2, written before the run)

Pooled per-half O/U log loss (lines 0.5/1.5/2.5) must NOT worsen vs
the uncorrected thinned baseline by more than 0.0005 in either half,
AND per-half Over-1.5 calibration error must be within ~1pp
(|err| ≤ 1.0pp) in BOTH halves, on the validation window
2023/24–2025/26 (top-5, n = 5,255). The candidate is selected on the
tuning window only (2020/21–2022/23 under the same refit harness,
n = 5,488) and validated ONCE.

## Harness (what changed vs V2)

- Fits use the production machinery exactly: `model_v2.DC` as
  `predict_upcoming_refactored.py` drives it — 7-tuples with xG from
  `features._load_xg_map()`, HL = 270 (`v2_config.json`), blend mode
  (production default), `games[-4000:]`.
- MONTHLY refits: per division, a fit at every month-start cutoff
  2020-08-01..2026-06-01 on games before the cutoff; a match is
  predicted by its month-start fit. (Production refits weekly with
  cutoff = run date; month-start fits exclude same-month earlier
  matches — a slight conservatism.)
- Frozen shares unchanged: 1H home 0.4419, away 0.4440.

## Step 1 — FT-level check: the drift hypothesis is CONFIRMED

Same 5,255 test matches, FT Over-2.5 calibration (actual rate 53.78%):

| Harness | Mean pred | Error |
|---------|-----------|-------|
| Static fit ≤2022/23 (production blend machinery) | 50.00% | **−3.78pp** |
| Monthly-refit harness | 52.60% | **−1.18pp** |

(V2's −4.73pp was a goals-only HL-365 static fit; the like-for-like
static comparator here is −3.78pp. Either way, most of the drift is a
static-harness artefact, as suspected.)

Per-half mean residuals (pred half total − actual), test window:
**1H −0.005, 2H −0.012** — vs V2's static −0.072 / −0.097. Under
refits, the inherited mean bias is essentially gone.

## Step 2 — Tuning (candidates fitted on tuning predictions only)

| Cand | Params | 1H LL | 1H calib | 2H LL | 2H calib | Tuning gate |
|------|--------|-------|----------|-------|----------|-------------|
| (a) none | — | 0.5496 | −1.10pp | 0.5596 | +0.09pp | FAIL (1H calib, by 0.10pp) |
| (b) scale | s: 1H 1.0460, 2H 0.9992 | 0.5488 | +0.89pp | 0.5596 | +0.05pp | **PASS** |
| (c) rho | rho: 1H 0.00, 2H +0.02 | 0.5495 | −1.82pp | 0.5593 | −0.97pp | FAIL |
| (d) NB | r = 1200 both halves | 0.5495 | −1.83pp | 0.5593 | −0.75pp | FAIL |

Winner by the pre-registered selection rule: **(b)**, the only tuning
passer. Note the tuning window itself still carried a small 1H mean
shortfall under refits (residual −0.056) — that is what the 1.046
scale fitted to.

## Step 3 — Validation (run once, on the selected winner)

| Row | 1H LL | ΔLL 1H | 1H calib | 2H LL | ΔLL 2H | 2H calib |
|-----|-------|--------|----------|-------|--------|----------|
| (a) baseline | 0.5333 | — | +0.22pp | 0.5599 | — | −0.71pp |
| (b) winner | 0.5338 | **+0.00054** | **+2.24pp** | 0.5599 | +0.00002 | −0.75pp |

## Verdict: GATE FAIL — no production change

The selected winner (b) fails both 1H legs on validation: the LL
delta (+0.000541) is a hair over the +0.0005 limit, and the 1H
Over-1.5 calibration (+2.24pp) is well outside 1pp. 2H passes both
legs. The 1.046 scale repaired a tuning-window 1H shortfall that did
not persist into the validation window (test 1H residual −0.005) —
the same failure shape as V2, at a much smaller magnitude: a
correction fitted on one window chasing that window's bias.

The uncomfortable fact, stated plainly: the uncorrected baseline (a)
satisfies both gate legs on the validation window (calib +0.22pp /
−0.71pp; LL delta 0 by construction). It is NOT shipped, because it
was eliminated at the tuning-selection stage (1H calib −1.10pp) and
selecting it now would be choosing the product on the validation
window — the gate would no longer mean anything. Its validation
numbers are on record in the aggregates and the per-match CSV.

## Next honest lever (not run)

A new pre-registered experiment (V4) with the product fixed in
advance as the UNCORRECTED thinned baseline under the refit harness —
no correction candidates, no tuning selection — judged by the same
gate on a window no selection has touched: the 2026/27 season. That
holdout currently holds only 452 labelled top-5 matches (through
2026-11-02), where a ±1pp calibration gate is mostly noise (SE of a
proportion ≈ 2.2pp); it becomes a meaningful test around n ≈ 1,500
(roughly February 2027), or earlier if the gate is judged with the
noise stated. Weekly (rather than monthly) refits would match
production even more closely and are computationally cheap.

Production untouched. No predictions_goals_halves_upcoming.csv built.
