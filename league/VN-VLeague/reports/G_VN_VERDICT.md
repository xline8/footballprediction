# Verdict — G-VN (Vietnam V-League goals, Dixon–Coles goals-only)

**FAIL — Gate Zero fails the dev gate on two of three legs. Virgin NOT
read. Nothing ships.**

Dev (season-blocked walk-forward; train seed 2021, 84 finished matches;
pooled n = 654):

| Arm | 1X2 LL | RPS | OU2.5 LL |
|---|---|---|---|
| Gate Zero | 1.0964 | 0.2236 | 0.7413 |
| SHRINK | 1.0964 | 0.2236 | 0.7413 |
| Climatology | 1.1056 | 0.2230 | 0.6884 |
| Naive trailing-10 | 1.1766 | 0.2434 | 0.8029 |

Per-season Gate Zero vs climatology (1X2 LL / RPS / OU2.5 LL):

| Season | n | Gate Zero | Climatology |
|---|---|---|---|
| 2022 | 156 | 1.1577 / 0.2464 / 0.8563 | 1.1326 / 0.2297 / 0.6943 |
| 2023 | 134 | 1.0967 / 0.2103 / 0.6932 | 1.1401 / 0.2190 / 0.6804 |
| 2023/2024 | 182 | 1.0825 / 0.2297 / 0.7092 | 1.0671 / 0.2251 / 0.6891 |
| 2024/2025 | 182 | 1.0575 / 0.2079 / 0.7102 | 1.0957 / 0.2179 / 0.6886 |

Gate arithmetic (PREREG_G_VN): pooled 1X2 LL beats climatology ✓
(1.0964 < 1.1056); pooled RPS beats climatology ✗ (0.2236 > 0.2230,
worse by 0.0007); pooled OU2.5 LL beats the base-rate baseline ✗
(0.7413 > 0.6884, worse by 0.0529). **Dev gate FAILS on the RPS and
OU2.5 legs.** Per the frozen rule, Gate Zero failing dev makes the
variants moot: SHRINK is not judged further, and the virgin
(2025/2026) is NOT read. `results_virgin.json` records the not-read
state.

## Why it failed (diagnosis, not a rescue)

- The totals leg fails in **all four dev seasons**, not one bad year
  (0.856 / 0.693 / 0.709 / 0.710 vs climatology 0.694 / 0.680 / 0.689 /
  0.689). The failure is systematic.
- The OU2.5 *level* is fine: mean predicted over-rate per season is
  0.415 / 0.426 / 0.443 / 0.452 against actual 0.455 / 0.418 / 0.451 /
  0.451. The damage is in the match-level spread — the model's
  over-probabilities vary far more than the outcomes warrant, so
  confident totals calls are punished in log loss. The DC's fitted
  team-rating spread is too wide for this league.
- Plausible contributors, all measured in EDA: the 2022 fold trains
  on only 84 seed matches (the truncated 2021 season), giving the
  worst OU LL of the four folds (0.856); the defence trait is weak
  (split-half r_GA mean 0.13 vs r_GF 0.52), so defence ratings are
  mostly noise that still moves lambdas; the draw rate is volatile
  across seasons (0.14–0.37), which also costs the RPS leg (lost by
  only 0.0007 pooled, with the 1X2 LL leg passing).
- The ratings do carry signal: Gate Zero beats the naive trailing-10
  baseline clearly on every metric (pooled LL 1.0964 vs 1.1766, RPS
  0.2236 vs 0.2434, OU 0.7413 vs 0.8029), and wins the 1X2 LL leg
  against climatology. The model is better than recent form and
  better than nothing on outcomes — just not better than the base
  rate on totals, and not better than climatology on RPS. That is
  exactly what the three-leg gate is for.
- SHRINK is byte-identical to Gate Zero in every season (0 changed
  rows, 0 thin-history teams), exactly as EDA F13 predicted: no team
  falls in the 1–5 prior-match band at any target-season start.

## Verification (independent of Codex)

- Pooled metrics recomputed from `results_dev.csv` per-row columns
  reproduce `results_dev.json` exactly (LL 1.0964, RPS 0.2236, OU
  0.7413; climatology 1.1056 / 0.2230 / 0.6884). Probabilities sum
  to 1 on all 654 rows; SHRINK columns are identical to Gate Zero's.
- A from-scratch re-implementation of the production DC pattern
  (written from the `model_v2.py` spec, not from the VN engine)
  reproduces the harness fold numbers exactly to 4dp on two folds:
  2022 LL 1.1577 / RPS 0.2464 / OU 0.8563 and 2024/2025 LL 1.0575 /
  RPS 0.2079 / OU 0.7102, with matching rho (0.0 / −0.10) and mu
  (1.1653 / 1.3029). The dev FAIL is genuine, not an engine bug.
- Fit bookkeeping checks out: cutoffs are each target season's first
  match date (2022-02-25, 2023-02-03, 2023-10-20, 2024-09-14);
  training counts 84 / 240 / 374 / 556 are the exact expanding
  sums; no 2025/2026 row appears in any dev output (asserted in the
  harness and re-checked from the files).
- `dc.py` / `arms.py` differ from the KZ reference by their
  docstring only; `harness.py` differs only by the intended VN
  adaptations (seasons, virgin guard, halves constant 0.4468).

## Ships

Nothing. No fitted params, no virgin predictions, no daily-runner
artefact. S/C/K/T were already not buildable (separate prereg).
League completion state: all buildable candidates (G-VN only) through
their gates — **league complete with 0 of 1 candidates passing
(0 markets live)**.
