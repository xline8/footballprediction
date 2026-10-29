# Experiment: Dixon-Coles Fit on xG vs Goals (Out-of-Sample 1X2)

One-off experiment. The first half changed no production code: `model_v2.py`
still fitted on goals. The second half records the go-live gates that later
flipped the default.

**Question.** Does fitting Dixon-Coles on expected goals, or on a blend of
goals and xG, improve out-of-sample 1X2 prediction over fitting on goals?

## Step 0 — xG coverage audit

Source: `xg_raw/xg_matches.csv` (genuine Understat data, read via
`features._load_xg_map`). No mock rows exist in the cache (`grep -ci mock`
returns 0), so the `_mock_xg` fallback never entered the local data. Rows
join to `all_matches_clean.csv` on (division, date, home, away) with team
names normalised on both sides: 16,408 top-5 matches, 16,085 joined (98.0%).

| League | Seasons | Matched | Total | % |
|---|---|---|---|
| E0 | 2017/18–2025/26 | 380 × 9 | 380 × 9 | 100.0 |
| SP1 | 2017/18 | 377 | 380 | 99.2 |
| SP1 | 2018/19–2025/26 | ~378–380 | 380 | 99.5–100 |
| D1 | 2017/18–2025/26 | 305–306 | 306 | 99.7–100 |
| I1 | 2017/18–2025/26 | 378–380 | 380 | 99.5–100 |
| F1 | 2017/18–2025/26 | 279–380 | 279–380 | 97.4–100 |
| All | 2026/27 (partial) | 0 | — | 0.0 |

Coverage is effectively complete for 2017/18–2025/26 in every league. The
running 2026/27 season has no xG yet and was excluded, with no imputation.

## Variants

All variants use identical folds: monthly walk-forward (`hl=270`,
`freq='m'`, `MAX_TRAIN=4000`, the production settings), tested on
2021/22–2025/26. Every test group sits strictly after its training cutoff.

- **G** — goals. The production control.
- **X** — pure xG. Team ratings are fitted on xG for/against. Rho is not
  estimated from xG "scorelines"; the goal-fitted rho from the same
  training window is reused.
- **B** — blend. The observed quantity is 0.5·goals + 0.5·xG, with the
  mixing weight fixed a priori, not tuned on the test folds.

## Results — overall (test 2021/22–2025/26, n = 8,889)

| Variant | Log loss | Brier |
|---|---|---|
| G | 0.99304 | 0.59160 |
| X | 0.98678 | 0.58803 |
| B | 0.98624 | 0.58765 |

## Results — per league (log loss)

| League | G | X | B | n |
|---|---|---|---|---|
| E0 | 0.98100 | 0.97736 | 0.97594 | 1,900 |
| SP1 | 0.98542 | 0.97728 | 0.97797 | 1,897 |
| D1 | 1.00485 | 0.99122 | 0.99273 | 1,529 |
| I1 | 0.99354 | 0.99021 | 0.98841 | 1,897 |
| F1 | 1.00406 | 1.00037 | 0.99896 | 1,666 |

X and B beat G in all five leagues.

## Paired bootstrap (10,000 resamples, per-match log-loss difference vs G)

| Pair | Mean | 95% CI | Excludes 0 |
|---|---|---|---|
| X − G | −0.00626 | [−0.00994, −0.00275] | yes |
| B − G | −0.00681 | [−0.00899, −0.00482] | yes |

## Adoption gate (vs G)

| Gate | X | B |
|---|---|---|
| Overall log loss below G | yes (0.98678 < 0.99304) | yes (0.98624 < 0.99304) |
| 95% CI of the difference excludes 0 | yes | yes |
| Any league worse by more than 0.005 | 0 leagues | 0 leagues |
| **Verdict** | **PASS** | **PASS** |

## Verdict and recommendation

Both variants pass. B, the 0.5 goals + 0.5 xG blend, is best overall: the
lowest log loss (0.98624) and the narrowest bootstrap interval (−0.00681
[−0.00899, −0.00482]). Pure xG (X) is close behind at 0.98678.

Recommendation: move the production fit to B. The experiment itself did not
make that switch. Two checks were named as prerequisites: confirmation on
the 2019/20–2020/21 validation fold, and the effect on derivative markets
(O/U, BTTS), whose prices shift with the model lambdas.

---

# Go-Live Gates (Production Switch to B)

`model_v2.py` gained a `DC_FIT_MODE` flag (`goals` | `blend`, environment
override `FOOTBALL_DC_FIT_MODE`). Under `blend`, the observed quantity is
0.5·goals + 0.5·xG where xG exists and goals otherwise; rho is always
selected on the goals fit of the same window. Three gates ran before the
default was flipped. All passed.

## Gate A — Meta stack (blend vs goals)

`records_cache.jsonl` was rebuilt under both modes on an identical universe
(production `cache_records`), the 9-logit meta model refitted with monthly
walk-forward, and stacked 1X2 log loss compared.

| Mode | Stacked log loss | n |
|---|---|---|
| goals | 1.00166 | 68,763 |
| blend | 1.00165 | 68,763 |

PASS (blend ≤ goals).

## Gate B — Derivatives (G vs B, experiment fold 2021/22–2025/26)

Over/Under 2.5 and BTTS priced from each variant's scoreline matrix.

| Market | LL goals | LL blend | Δ | Brier goals | Brier blend | n |
|---|---|---|---|---|---|---|
| Over 2.5 | 0.68370 | 0.67775 | −0.00595 | 0.24495 | 0.24237 | 8,889 |
| BTTS | 0.69088 | 0.68464 | −0.00624 | 0.24823 | 0.24577 | 8,889 |

PASS (both markets improve; the degradation allowance was +0.002).

## Gate C — Held-out seasons (2017/18–2020/21)

| Mode | Log loss | n |
|---|---|---|
| goals | 1.02333 | 7,196 |
| blend | 0.99300 | 7,196 |

PASS (blend ≤ goals, Δ −0.03034).

## Verdict

All three gates passed, so the `DC_FIT_MODE` default was flipped to
`blend`. End-to-end verification: `test_core.py` passes, the full
`--run-all` pipeline exits 0, the cups step runs 13/13, and the records
cache was rebuilt under blend (`records_cache.meta.json` stamped
`{"dc_fit_mode":"blend"}`).

Gate runtime: about 983 seconds (two full cache rebuilds). Runner:
`go_live_gates.py`.
