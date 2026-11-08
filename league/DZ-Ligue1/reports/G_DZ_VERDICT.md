# Verdict — G-DZ (Algeria Ligue 1 goals model)

**FAIL at the dev gate — on the OU2.5 leg only. Nothing ships.
Virgin 2025/2026 deliberately NOT read.**

Prereg `league/DZ-Ligue1/prereg/PREREG_G_DZ.md` precedes all
fitting (written to disk before the engine ran; see the git-freeze
note in the prereg — the coordinator will commit the branch after
rebuilding git history). Branch `build/dz-ligue1`. Engine
`league/DZ-Ligue1/engine/goals/`; dev results
`results_dev.json` (+ CSV, `predictions_dev.csv`).

## Dev results (season-blocked expanding walk-forward, n=719)

| arm | season | kind | n | 1X2 LL | RPS | OU2.5 LL |
|---|---|---|---|---:|---:|---:|
| Gate Zero | 2022/2023 | model | 240 | 0.977440 | 0.195716 | 0.677097 |
| Gate Zero | 2022/2023 | climatology | 240 | 0.989854 | 0.197521 | 0.661565 |
| Gate Zero | 2022/2023 | naive trailing-10 | 240 | 1.061363 | 0.219139 | 0.728400 |
| Gate Zero | 2023/2024 | model | 239 | 1.015627 | 0.207753 | 0.701190 |
| Gate Zero | 2023/2024 | climatology | 239 | 1.030694 | 0.213804 | 0.681525 |
| Gate Zero | 2023/2024 | naive trailing-10 | 239 | 1.119350 | 0.239073 | 0.749632 |
| Gate Zero | 2024/2025 | model | 240 | 1.003602 | 0.193226 | 0.665511 |
| Gate Zero | 2024/2025 | climatology | 240 | 1.044045 | 0.206757 | 0.648498 |
| Gate Zero | 2024/2025 | naive trailing-10 | 240 | 1.027451 | 0.199481 | 0.711050 |
| **Gate Zero** | **pooled** | **model** | **719** | **0.998866** | **0.198886** | **0.681238** |
| **Gate Zero** | **pooled** | **climatology** | **719** | **1.021518** | **0.206016** | **0.663838** |
| **Gate Zero** | **pooled** | **naive trailing-10** | **719** | **1.069319** | **0.219203** | **0.729666** |
| SHRINK | pooled | model | 719 | 0.998866 | 0.198886 | 0.681238 |

SHRINK is **identical to Gate Zero on all 719 dev rows** (0 changed
prediction rows in every fold; 0 target teams in the 1–5 prior-match
band in every fold). Under season-blocked date-cutoff fitting a
team either has 0 prior in-league matches (promoted, n=0 → shrink
factor 0 → league mean, same as Gate Zero) or full prior seasons
(≥239 matches) — the 1–5 band never occurs. Same structural finding
as G-GH, G-RU2, G-NG and G-SV.

## Gate arithmetic (mechanical, per prereg)

Dev gate — pooled model must beat climatology on 1X2 LL and RPS, and
beat the base rate on OU2.5 LL:

- 1X2 LL: 0.998866 vs 1.021518 — model **wins by −0.022652** ✓
- RPS: 0.198886 vs 0.206016 — model **wins by −0.007130** ✓
- OU2.5 LL: 0.681238 vs 0.663838 — model **loses by +0.017400** ✗

Gate Zero passes two of three legs and fails the OU2.5 leg; SHRINK
fails identically. Per the frozen rule ("If Gate Zero fails its own
dev gate, variants are moot, verdict FAIL, virgin NOT read"), **no
virgin leg is evaluated and the virgin window stays unread** — no
`results_virgin.json`, no `fitted_params_virgin.json`, no virgin
predictions file exists.

Fold reading: the model beats climatology on LL and RPS in **all 3**
folds, and beats the naive trailing-10 baseline pooled on all three
legs (LL 0.999 vs 1.069; RPS 0.199 vs 0.219; OU 0.681 vs 0.730) — but
it loses the OU leg in **all 3 folds** (0.677 vs 0.662; 0.701 vs
0.682; 0.666 vs 0.648), so the OU failure is systematic, not one bad
fold. At 2.19 goals/match with a 38.0% over-2.5 base rate, the pooled
over-rate is a hard bar, and the DC's total-goals distribution —
fitted to win the 1X2 — is worse than the base rate at calling the
2.5 line in every season. The 1X2/RPS wins (−0.023 LL, −0.007 RPS)
are respectable for a scores-only league (between SV's −0.033 and
Ghana's failure), consistent with EDA §2's moderate attack trait
(r=.40 pooled, rising to .64) — but the gate is binary and the OU
leg is failed, so the verdict stands. The margin (+0.017 on OU LL,
larger than SV's +0.010) is recorded honestly for the program's
cross-league record.

Two fitted-parameter notes (from the independent second-path fit):
fitted home advantage h = 0.436 / 0.584 / 0.467 across the three
folds — far above production's init 0.28 — so the DC *does* learn
this league's very large home edge (+0.51 goals); the OU failure is
not a missed home effect. Fitted rho = −0.05 / −0.10 / 0.0.

## Verification (independent of the implementor)

- `dc.py` is byte-identical to SV's `dc.py` except the docstring;
  `arms.py` likewise. `harness.py` differs from SV's only in the
  sanctioned constants (data file, seasons/counts, virgin n=240,
  halves constant 0.4421, leg-(iii) threshold 2 of 3, predictions
  filename) — verified by diff (31 changed lines, all DZ
  adaptations).
- Dev re-run reproduces `results_dev.json` exactly (md5-verified);
  an independent second-path recomputation (fresh code fitting
  production `model_v2.DC` per fold, climatology and naive
  trailing-10 reimplemented independently) reproduces every pooled
  and per-fold metric to 6 decimal places and the same gate outcome
  (LL ✓, RPS ✓, OU ✗).
- Dev predictions contain only the three dev seasons (1,438 rows =
  719 × 2 arms); no 2025/2026 or 2026/2027 row exists.
- `virgin()` was exercised and raises `RuntimeError` ("Gate Zero
  failed the dev gate; virgin evaluation is prohibited") before
  reading any virgin row — the gate check works as frozen.
- Data builder re-run regenerates identical CSVs (1,332 rows, 1,331
  eligible, per-season counts as frozen in the prereg); EDA numbers
  re-run reproduces `eda_numbers.json` exactly; headline levels and
  the HT share were recomputed from the raw payloads by a second
  path and match exactly.
- Environment note: during this build (2026-11-10) git history was
  damaged repo-wide by a coordinator cleanup command (~15:42 WIB)
  and all git work was frozen by the coordinator. NO commits exist
  for this branch — every artifact below is filed on disk in the
  worktree `~/workspace/wt-dz-ligue1` (branch `build/dz-ligue1`
  checked out before the freeze). The coordinator will rebuild
  history and commit/merge afterwards. Commit order is preserved
  in substance: the prereg files were written before any engine
  fitting began, and no virgin row was read at any point.

## What ships

Nothing. No fitted params, no predictions, no daily-runner
activation. The virgin window 2025/2026 stays unread and the
confirmatory window 2026/2027 stays reserved. League completion
state: **complete** — the only buildable candidate (G-DZ) ran its
full gate and failed; S/C/K/T are not buildable (separate report).
