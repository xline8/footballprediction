# C-J1 Verdict — J1 corners model

Date: 2026-11-09. Branch `build/c-j1`. Prereg:
`league/J1/prereg/PREREG_C_J1.md` (commit
c9e1c809d66f38997aeb4a15403d0c2ea1645a61, frozen before any fitting).
Engine: `league/J1/engine/corners/`. Implementation by Codex
(gpt-5.6-luna) under the two-agent flow; all numbers below were
reproduced end-to-end by the coordinator's own rerun (dev results,
virgin results, and the predictions CSV are byte-identical to
Codex's), and 5 virgin predictions were recomputed by hand from the
fitted parameters with independent code (max diff 2.5e-14).

## Verdict: PASS (calibration provisional) — Gate Zero ships

Both arms pass the dev gate and all virgin legs. Their virgin
predictions are literally identical — on the full 2021–2025
training window both arms' fitted territorial betas are 0, so both
reduce to the shared core engine (gamma = 0.15, r = 1.1539) — and
the frozen both-pass rule breaks the virgin-LL tie in favour of
Gate Zero, the simpler production-proven arm. The predictions CSV
on file is Gate Zero's, `arm = gate_zero`.

The honest reading of the arm comparison: the box-touch multiplier
never earned a nonzero coefficient. Arm X7's training grid selected
beta_bt = 0 at **every** fit (2022, 2023, 2024, 2025, and the virgin
fit), so the X7 multiplier was active on 0% of matches despite the
covariate being available for both teams in 27–97% of matches per
season. X7's small dev edge over Gate Zero (pooled LL@9.5 0.6915 vs
0.6935) is not a box-touch effect: it comes from Gate Zero's own
big-chance beta (+0.025 in the 2022–2024 fits) slightly hurting
Gate Zero in 2023–2024, seasons where X7 — running multiplier-free —
did not pay that cost. EDA F9's trait (r = 0.857) is real as a team
trait; at trailing-10 window scale, inside this multiplier
structure, it adds nothing the grid will pay for. That is a result,
not a near-miss to tune around: any retry is a new prereg.

## Dev results (walk-forward, season-blocked hyperparameter fits; n = 1,372)

LL@9.5 is the primary line; LL@8.5 / LL@10.5 reported per prereg.
Mean predicted vs actual over-9.5 rate on the pooled window: model
46.9% vs actual 49.3%; base rate 35.6%; naive 36.7% (both baselines
run cold because the decay-weighted / trailing levels lag the
2023–2024 corner rise).

| Season | n | Arm / baseline | LL@8.5 | LL@9.5 | LL@10.5 |
|---|---|---|---|---|---|
| 2022 | 306 | Gate Zero | 0.6819 | 0.6801 | 0.6248 |
| 2022 | 306 | X7 | 0.6867 | 0.6846 | 0.6282 |
| 2022 | 306 | League base rate | 0.7500 | 0.6974 | 0.6273 |
| 2022 | 306 | Naive trailing-10 | 0.7496 | 0.6966 | 0.6243 |
| 2023 | 306 | Gate Zero | 0.6737 | 0.7067 | 0.6825 |
| 2023 | 306 | X7 | 0.6680 | 0.7009 | 0.6809 |
| 2023 | 306 | League base rate | 0.7864 | 0.7522 | 0.6900 |
| 2023 | 306 | Naive trailing-10 | 0.7631 | 0.7357 | 0.6783 |
| 2024 | 380 | Gate Zero | 0.6403 | 0.6984 | 0.6841 |
| 2024 | 380 | X7 | 0.6341 | 0.6922 | 0.6775 |
| 2024 | 380 | League base rate | 0.7907 | 0.7594 | 0.6956 |
| 2024 | 380 | Naive trailing-10 | 0.7578 | 0.7379 | 0.6835 |
| 2025 | 380 | Gate Zero | 0.6687 | 0.6889 | 0.6497 |
| 2025 | 380 | X7 | 0.6687 | 0.6889 | 0.6497 |
| 2025 | 380 | League base rate | 0.7465 | 0.7174 | 0.6550 |
| 2025 | 380 | Naive trailing-10 | 0.7447 | 0.7114 | 0.6540 |
| Pooled | 1372 | Gate Zero | 0.6649 | 0.6935 | 0.6610 |
| Pooled | 1372 | X7 | 0.6630 | 0.6915 | 0.6596 |
| Pooled | 1372 | League base rate | 0.7684 | 0.7323 | 0.6679 |
| Pooled | 1372 | Naive trailing-10 | 0.7535 | 0.7209 | 0.6609 |

Dev gate (pooled LL@9.5 must beat BOTH baselines): Gate Zero
**PASS** (0.6935 < 0.7209 and < 0.7323). X7 **PASS** (0.6915 <
0.7209 and < 0.7323). Both arms therefore read the virgin window.

Fitted hyperparameters per target season (both arms share gamma
and r; they differ only in the multiplier betas):

| Fit for | gamma | r | Gate Zero beta (poss, bc) | X7 beta (bt) | X7 both-active |
|---|---|---|---|---|---|
| 2022 | 0.15 | 1.0855 | (0, +0.025) | 0 | 27.5% |
| 2023 | 0.15 | 1.1457 | (0, +0.025) | 0 | 22.9% |
| 2024 | 0.15 | 1.1595 | (0, +0.025) | 0 | 89.7% |
| 2025 | 0.15 | 1.1575 | (0, 0) | 0 | 96.6% |
| 2026 (virgin) | 0.15 | 1.1539 | (0, 0) | 0 | 88.5% |

Possession's beta is 0 in every Gate Zero fit as well; the only
nonzero territorial coefficient anywhere in this candidate is the
small big-chance beta in the three early fits, and it does not
survive to the full-window fits.

## Virgin results (season "2026", n = 200, read once after dev froze)

Actual over-9.5 rate 45.5% (mean total corners 9.455).

| Arm / baseline | LL@8.5 | LL@9.5 | LL@10.5 | Mean P(over 9.5) | Calib diff | SE |
|---|---|---|---|---|---|---|
| Gate Zero | 0.6858 | 0.6901 | 0.6302 | 48.09% | +2.59pp | 3.53pp |
| X7 | 0.6858 | 0.6901 | 0.6302 | 48.09% | +2.59pp | 3.53pp |
| League base rate | 0.7356 | 0.7050 | 0.6272 | 36.78% | — | — |
| Naive trailing-10 | 0.7371 | 0.7059 | 0.6235 | 36.19% | — | — |

## Per-leg verdicts

| Leg | Gate Zero | X7 |
|---|---|---|
| Dev gate (pooled LL@9.5 beats both baselines) | PASS (0.6935) | PASS (0.6915) |
| Virgin (i) LL@9.5 ≤ Gate Zero's and ≤ best baseline's (0.7050) | PASS (0.6901) | PASS (0.6901, equal to Gate Zero) |
| Virgin (ii) calibration ≤1.0pp, breach ≤1 SE = provisional | PROVISIONAL PASS (breach 1.59pp ≤ SE 3.53pp) | PROVISIONAL PASS (same) |
| Virgin (iii) dev sign check (LL ≤ Gate Zero in ≥2 of 4 seasons) | n/a (comparator) | PASS (3/4: 2023, 2024, 2025-tie; 2022 worse) |
| **Overall** | **PASS (provisional)** | **PASS (provisional)** |

Both-pass rule: both arms pass, pooled virgin LL@9.5 is tied
(0.690118 for both, predictions identical), and the prereg's tie
rule ships the simpler arm — **Gate Zero ships**. C-J1 is the
first J.League candidate to ship an arm; it launches
predictions-only (no J.League odds/settlement source in-system,
per the design's scope note for J1 products).

## Verification notes (coordinator, independent of Codex)

- Full harness rerun by the coordinator reproduces every number
  above exactly: `results_dev.json`, `results_virgin.json`, and
  `c_j1_virgin_predictions.csv` are byte-identical to Codex's run.
- Virgin isolation confirmed in code: the dev path loads only
  seasons 2021–2025 (season filter at load in `core.load`, dev
  season set in `harness`); season "2026" is read only inside the
  virgin path, which additionally refuses any arm that fails the
  persisted dev gate.
- Spot check: 5 virgin matches (2026-02-06, 03-14, 04-11, 05-06,
  06-06) recomputed by hand from `fitted_params_virgin.json` with
  independent code (own decay-weighted base rates, rolling-5
  factors, NB pmf) match the CSV on mu, P(over 8.5), P(over 9.5),
  mu_1h, 1H and 2H ladder probabilities — max diff 2.5e-14. The
  1H/2H values equal the frozen 0.447 / 0.553 split of the same FT
  mu at the same r, as specified.
- One coordinator correction during verification, numerically a
  no-op: Codex's naive-baseline trailing window updated its history
  match-by-match within a date, while the prereg requires
  strictly-pre-date state throughout. The history update is now
  date-grouped like the rest of the engine (comment in
  `core.attach_naive`). It cannot change any number — verified in
  the data that no team plays twice on one date, so a team's own
  trailing history never contained a same-date entry — and the
  rerun after the fix is byte-identical, as expected.
- Codex could not commit from its sandbox (worktree index
  read-only there); the coordinator commits the engine, results,
  predictions, and this verdict on `build/c-j1`. No push, no merge;
  `league/PROGRAM_STATUS.md` untouched per instructions.
