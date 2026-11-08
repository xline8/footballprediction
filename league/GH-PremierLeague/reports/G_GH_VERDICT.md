# Verdict — G-GH (Ghana Premier League goals model)

**FAIL at the dev gate. Nothing ships. Virgin 2025/2026 deliberately NOT read.**

Prereg `league/GH-PremierLeague/prereg/PREREG_G_GH.md` (commit
`577fae30`) precedes all fitting. Branch `build/gh-premier-league`.
Engine `league/GH-PremierLeague/engine/goals/`; dev results
`results_dev.json` (+ CSV, `predictions_dev.csv`).

## Dev results (season-blocked expanding walk-forward, n=901)

| arm | season | kind | n | 1X2 LL | RPS | OU2.5 LL |
|---|---|---|---:|---:|---:|---:|
| Gate Zero | 2022/2023 | model | 306 | 0.965713 | 0.191606 | 0.659221 |
| Gate Zero | 2022/2023 | climatology | 306 | 0.953622 | 0.188389 | 0.656701 |
| Gate Zero | 2022/2023 | naive trailing-10 | 306 | 1.012274 | 0.205448 | 0.683273 |
| Gate Zero | 2023/2024 | model | 305 | 0.985199 | 0.196877 | 0.666954 |
| Gate Zero | 2023/2024 | climatology | 305 | 0.961255 | 0.191323 | 0.637286 |
| Gate Zero | 2023/2024 | naive trailing-10 | 305 | 1.018128 | 0.208577 | 0.746721 |
| Gate Zero | 2024/2025 | model | 290 | 0.967141 | 0.188361 | 0.640857 |
| Gate Zero | 2024/2025 | climatology | 290 | 0.982011 | 0.194757 | 0.603696 |
| Gate Zero | 2024/2025 | naive trailing-10 | 290 | 1.049913 | 0.210238 | 0.746213 |
| **Gate Zero** | **pooled** | **model** | **901** | **0.972769** | **0.192346** | **0.655928** |
| **Gate Zero** | **pooled** | **climatology** | **901** | **0.965343** | **0.191432** | **0.633068** |
| **Gate Zero** | **pooled** | **naive trailing-10** | **901** | **1.026370** | **0.208049** | **0.725009** |
| SHRINK | pooled | model | 901 | 0.972769 | 0.192346 | 0.655928 |

SHRINK is **identical to Gate Zero on all 901 dev rows** (0 changed
prediction rows in every fold; 0 target teams in the 1–5 prior-match
band in every fold). Under season-blocked date-cutoff fitting a team
either has 0 prior in-league matches (promoted, n=0 → shrink factor
0 → league mean, same as Gate Zero) or a full prior season (≥34) —
the 1–5 band never occurs. Same structural finding as G-RU2 and G-NG.

## Gate arithmetic (mechanical, per prereg)

Dev gate — pooled model must beat climatology on 1X2 LL and RPS, and
beat the base rate on OU2.5 LL:

- 1X2 LL: 0.972769 vs 0.965343 — model **loses by +0.007426** ✗
- RPS: 0.192346 vs 0.191432 — model **loses by +0.000914** ✗
- OU2.5 LL: 0.655928 vs 0.633068 — model **loses by +0.022860** ✗

Gate Zero fails all three legs; SHRINK fails identically. Per the
frozen rule ("If Gate Zero fails its own dev gate, variants are moot,
verdict FAIL, virgin NOT read"), **no virgin leg is evaluated and
the virgin window stays unread** — no `results_virgin.json`, no
`fitted_params_virgin.json`, no virgin predictions file exists.

Fold reading: the model beats climatology on LL and RPS only in the
2024/2025 fold (0.967 vs 0.982; 0.188 vs 0.195) while losing OU there
too (0.641 vs 0.604); it loses all three legs in both 2022/2023 and
2023/2024. The model does beat the naive trailing-10 baseline pooled
on all three legs (LL 0.973 vs 1.026; RPS 0.192 vs 0.208; OU 0.656 vs
0.725) — but the gate is against climatology, and climatology wins
because Ghana is so low-scoring and home-heavy (2.02 goals/match,
57.1% home wins, 32.9% over-2.5 pooled) that the pooled base rates
are a hard bar and the DC ratings, fitted on a trait-free attack
side (EDA §2: split-half r=−.03 pooled), add more noise than signal.
The defence trait (r=.32) is not enough to carry the fit: the one
fold the model wins is the fold where the attack side happens to
cooperate, and even there the OU leg fails.

## Verification (independent of the implementor)

- `dc.py` is byte-identical to NG's `dc.py` except the docstring;
  `arms.py` likewise. Its lambdas reproduce the **production
  `model_v2.DC` class exactly** (max diff 0.0 over all 306 matches
  of the 2022/2023 fold; production rho 0.0, fitted home advantage
  h=0.616828 on the seed fit).
- `harness.py` differs from NG's only in the sanctioned constants
  (data file, seasons/counts, team keys by name, halves constant
  0.4622, virgin filename) — verified by diff.
- Dev re-run reproduces `results_dev.json` exactly (SHA-256
  `1a1e4139c07fe3ea6f4df1a1e88e63679816bcfc1277e5496ff3fa624ff67713`
  before and after re-run); an independent second-path recomputation
  (fresh code, CSVs only) reproduces every per-fold climatology and
  model metric to 6 decimal places and the pooled rows from the folds.
- Dev predictions contain only the three dev seasons (1,802 rows =
  901 × 2 arms); no 2025/2026 or 2026/2027 row was read (harness
  asserts the loaded seasons; `virgin()` raises `RuntimeError`
  before any virgin read — exercised and confirmed).
- Data builder re-run regenerates identical CSVs (1,619 rows, 1,596
  eligible, per-season counts as frozen in the prereg).
- No implementor artifacts needed correction: the engine port was
  clean on first review (the only diffs from NG are the frozen GH
  constants).

## What ships

Nothing. No fitted params, no predictions, no daily-runner
activation. The confirmatory window 2026/2027 stays reserved and
unread. League completion state: **complete** — the only buildable
candidate (G-GH) ran its full gate and failed; S/C/K/T are not
buildable (separate report).
