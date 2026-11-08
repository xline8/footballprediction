# Verdict — G-NG (Nigeria Professional Football League goals model)

**FAIL at the dev gate. Nothing ships. Virgin 2025/2026 deliberately NOT read.**

Prereg `league/NG-ProfessionalLeague/prereg/PREREG_G_NG.md` (commit
`f45177d7`) precedes all fitting. Branch `build/ng-professional-league`.
Engine `league/NG-ProfessionalLeague/engine/goals/`; dev results
`results_dev.json` (+ CSV, `predictions_dev.csv`).

## Dev results (season-blocked expanding walk-forward, n=939)

| arm | season | kind | n | 1X2 LL | RPS | OU2.5 LL |
|---|---|---|---:|---:|---:|---:|
| Gate Zero | 2023 | model | 180 | 0.966037 | 0.182140 | 0.684062 |
| Gate Zero | 2023 | climatology | 180 | 1.028562 | 0.198952 | 0.648260 |
| Gate Zero | 2023 | naive trailing-10 | 180 | 1.069432 | 0.204945 | 0.824846 |
| Gate Zero | 2023/2024 | model | 379 | 0.839731 | 0.157329 | 0.668232 |
| Gate Zero | 2023/2024 | climatology | 379 | 0.799027 | 0.144825 | 0.657234 |
| Gate Zero | 2023/2024 | naive trailing-10 | 379 | 0.833859 | 0.154150 | 0.719404 |
| Gate Zero | 2024/2025 | model | 380 | 0.896924 | 0.170988 | 0.661427 |
| Gate Zero | 2024/2025 | climatology | 380 | 0.876348 | 0.164737 | 0.642063 |
| Gate Zero | 2024/2025 | naive trailing-10 | 380 | 0.963904 | 0.181616 | 1.037758 |
| **Gate Zero** | **pooled** | **model** | **939** | **0.887088** | **0.167613** | **0.668512** |
| **Gate Zero** | **pooled** | **climatology** | **939** | **0.874318** | **0.163259** | **0.649374** |
| **Gate Zero** | **pooled** | **naive trailing-10** | **939** | **0.931644** | **0.175002** | **0.868450** |
| SHRINK | pooled | model | 939 | 0.887088 | 0.167613 | 0.668512 |

SHRINK is **identical to Gate Zero on all 939 dev rows** (0 changed
prediction rows in every fold; 0 target teams in the 1–5 prior-match
band in every fold). Under season-blocked date-cutoff fitting a team
either has 0 prior in-league matches (promoted, n=0 → shrink factor
0 → league mean, same as Gate Zero) or a full prior season (≥18) —
the 1–5 band never occurs. Same structural finding as G-RU2.

## Gate arithmetic (mechanical, per prereg)

Dev gate — pooled model must beat climatology on 1X2 LL and RPS, and
beat the base rate on OU2.5 LL:

- 1X2 LL: 0.887088 vs 0.874318 — model **loses by +0.012770** ✗
- RPS: 0.167613 vs 0.163259 — model **loses by +0.004354** ✗
- OU2.5 LL: 0.668512 vs 0.649374 — model **loses by +0.019138** ✗

Gate Zero fails all three legs; SHRINK fails identically. Per the
frozen rule ("If Gate Zero fails its own dev gate, variants are moot,
verdict FAIL, virgin NOT read"), **no virgin leg is evaluated and
the virgin window stays unread** — no `results_virgin.json`, no
`fitted_params_virgin.json`, no virgin predictions file exists.

Fold reading: the model beats climatology on LL and RPS only in the
2023 group-stage fold (0.966 vs 1.029; 0.182 vs 0.199) while losing
OU there too (0.684 vs 0.648); it loses all three legs in both full
seasons (2023/2024, 2024/2025). The model does beat the naive
trailing-10 baseline pooled on LL (0.887 vs 0.932) and RPS (0.168 vs
0.175) — but the gate is against climatology, and climatology wins
because the NPFL is so home-heavy and low-scoring (65.2% home wins,
35.6% over-2.5 pooled) that the pooled base rates are a hard bar and
the DC ratings, fitted on weak team traits (EDA §2: split-half
r=.17/.23 pooled), add more noise than signal.

## Verification (independent of the implementor)

- `dc.py` is byte-identical to RU2's `dc.py` except the docstring;
  its lambdas reproduce the **production `model_v2.DC` class exactly**
  (max diff 0.0 over all 180 matches of the 2023 fold; production
  rho 0.0, fitted home advantage h=0.9697 — the extreme home edge).
- Dev re-run reproduces `results_dev.json` exactly; an independent
  second-path recomputation (fresh code, CSVs only) reproduces every
  per-fold climatology and model metric to 0.0 and the pooled rows
  from the folds to <1e-14.
- Dev predictions contain only the three dev seasons; no
  2025/2026 or 2026/2027 row was read (harness asserts the loaded
  seasons; `virgin()` raises `RuntimeError` before any virgin read
  — exercised and confirmed).
- Data builder re-run regenerates byte-identical CSVs (1,830 rows,
  1,813 eligible, per-season counts as frozen in the prereg).
- Two implementor artifacts were corrected during review, not
  trusted: a duplicated `data/data/` CSV copy (removed) and a
  `virgin()` stub (ported in full from the RU2 pattern with NG
  constants — sign check ≥2 of 3 folds, halves constant 0.4796 —
  so the engine file is complete; it is unreachable in this build
  because the dev gate failed first). One inventory error was caught
  by the CSV audit: exactly one payload (4635917) carries a simple
  lineup — the Phase A docs were corrected (1/1,830, not 0).

## What ships

Nothing. No fitted params, no predictions, no daily-runner
activation. The confirmatory window 2026/2027 stays reserved and
unread. League completion state: **complete** — the only buildable
candidate (G-NG) ran its full gate and failed; S/C/K/T are not
buildable (separate report).
