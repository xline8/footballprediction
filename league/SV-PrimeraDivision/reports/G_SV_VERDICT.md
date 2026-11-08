# Verdict — G-SV (El Salvador Primera Division goals model)

**FAIL at the dev gate — on the OU2.5 leg only. Nothing ships.
Virgin 2025/2026 deliberately NOT read.**

Prereg `league/SV-PrimeraDivision/prereg/PREREG_G_SV.md` precedes all
fitting. Branch `build/sv-primera-division`. Engine
`league/SV-PrimeraDivision/engine/goals/`; dev results
`results_dev.json` (+ CSV, `predictions_dev.csv`).

## Dev results (tournament-blocked expanding walk-forward, n=815)

| arm | tournament | kind | n | 1X2 LL | RPS | OU2.5 LL |
|---|---|---|---:|---:|---:|---:|
| Gate Zero | 2021/2022 - Clausura | model | 132 | 1.108602 | 0.222395 | 0.707696 |
| Gate Zero | 2021/2022 - Clausura | climatology | 132 | 1.083931 | 0.215909 | 0.693147 |
| Gate Zero | 2021/2022 - Clausura | naive trailing-10 | 132 | 1.119571 | 0.224824 | 0.746400 |
| Gate Zero | 2022/2023 - Apertura | model | 67 | 1.073865 | 0.219508 | 0.679864 |
| Gate Zero | 2022/2023 - Apertura | climatology | 67 | 1.053554 | 0.213003 | 0.693215 |
| Gate Zero | 2022/2023 - Apertura | naive trailing-10 | 67 | 1.081032 | 0.221757 | 0.732108 |
| Gate Zero | 2022/2023 - Clausura | model | 132 | 1.068106 | 0.216079 | 0.678876 |
| Gate Zero | 2022/2023 - Clausura | climatology | 132 | 1.106507 | 0.228591 | 0.684098 |
| Gate Zero | 2022/2023 - Clausura | naive trailing-10 | 132 | 1.183372 | 0.246189 | 0.712755 |
| Gate Zero | 2023/2024 - Apertura | model | 132 | 1.055677 | 0.214660 | 0.763650 |
| Gate Zero | 2023/2024 - Apertura | climatology | 132 | 1.092316 | 0.227978 | 0.699870 |
| Gate Zero | 2023/2024 - Apertura | naive trailing-10 | 132 | 1.072987 | 0.219474 | 0.779070 |
| Gate Zero | 2023/2024 - Clausura | model | 132 | 1.049520 | 0.226936 | 0.678577 |
| Gate Zero | 2023/2024 - Clausura | climatology | 132 | 1.080278 | 0.235240 | 0.690275 |
| Gate Zero | 2023/2024 - Clausura | naive trailing-10 | 132 | 1.153738 | 0.257328 | 0.693798 |
| Gate Zero | 2024/2025 - Apertura | model | 110 | 1.012647 | 0.215419 | 0.708219 |
| Gate Zero | 2024/2025 - Apertura | climatology | 110 | 1.085126 | 0.240160 | 0.687748 |
| Gate Zero | 2024/2025 - Apertura | naive trailing-10 | 110 | 1.044682 | 0.226107 | 0.775276 |
| Gate Zero | 2024/2025 - Clausura | model | 110 | 1.022808 | 0.203710 | 0.665346 |
| Gate Zero | 2024/2025 - Clausura | climatology | 110 | 1.109957 | 0.234312 | 0.677400 |
| Gate Zero | 2024/2025 - Clausura | naive trailing-10 | 110 | 1.117179 | 0.230227 | 0.715091 |
| **Gate Zero** | **pooled** | **model** | **815** | **1.056516** | **0.217154** | **0.699441** |
| **Gate Zero** | **pooled** | **climatology** | **815** | **1.089531** | **0.228567** | **0.689457** |
| **Gate Zero** | **pooled** | **naive trailing-10** | **815** | **1.114295** | **0.233333** | **0.736219** |
| SHRINK | pooled | model | 815 | 1.056516 | 0.217154 | 0.699441 |

SHRINK is **identical to Gate Zero on all 815 dev rows** (0 changed
prediction rows in every fold; 0 target teams in the 1–5 prior-match
band in every fold). Under tournament-blocked date-cutoff fitting a
team either has 0 prior in-league matches (promoted, n=0 → shrink
factor 0 → league mean, same as Gate Zero) or full prior tournaments
(≥67 matches) — the 1–5 band never occurs. Same structural finding
as G-GH, G-RU2 and G-NG.

## Gate arithmetic (mechanical, per prereg)

Dev gate — pooled model must beat climatology on 1X2 LL and RPS, and
beat the base rate on OU2.5 LL:

- 1X2 LL: 1.056516 vs 1.089531 — model **wins by −0.033015** ✓
- RPS: 0.217154 vs 0.228567 — model **wins by −0.011413** ✓
- OU2.5 LL: 0.699441 vs 0.689457 — model **loses by +0.009984** ✗

Gate Zero passes two of three legs and fails the OU2.5 leg; SHRINK
fails identically. Per the frozen rule ("If Gate Zero fails its own
dev gate, variants are moot, verdict FAIL, virgin NOT read"), **no
virgin leg is evaluated and the virgin window stays unread** — no
`results_virgin.json`, no `fitted_params_virgin.json`, no virgin
predictions file exists.

Fold reading: the model beats climatology on LL and RPS in 5 of 7
folds (losing only the first two: 2021/2022 Clausura and the
shortened 2022/2023 Apertura) and on OU in 4 of 7 — but the OU
losses are concentrated where they hurt: the 2023/2024 Apertura
fold alone (model 0.764 vs climatology 0.700, the highest over-rate
tournament at 50.8%, which the model under-called) accounts for
most of the pooled OU deficit, with smaller OU losses in the first
two folds and 2024/2025 Apertura. The model beats the naive
trailing-10 baseline pooled on all three legs (LL 1.057 vs 1.114;
RPS 0.217 vs 0.233; OU 0.699 vs 0.736) — but the gate is against
climatology, and on the totals line climatology wins: at 2.51
goals/match with a 46.2% over-2.5 base rate, the pooled over-rate
is a hard bar, and the DC's total-goals distribution — fitted to
win the 1X2 — is slightly worse than the base rate at calling the
2.5 line. Unlike Ghana, this is a near miss on one leg, not a
three-leg failure: the 1X2/RPS wins are the largest of any
scores-only league built so far (LL −0.033, RPS −0.011), consistent
with EDA §2's moderately reliable attack/defence traits
(r=.37/.36 pooled, vs Ghana's trait-free attack). The gate is
binary and the OU leg is failed, so the verdict stands — but the
margin (0.010 on OU LL) is recorded honestly for the program's
cross-league record.

## Verification (independent of the implementor)

- `dc.py` is byte-identical to GH's `dc.py` except the docstring;
  `arms.py` likewise. Its lambdas reproduce the **production
  `model_v2.DC` class exactly** (max diff 0.0 over all 132 matches
  of the 2021/2022 - Clausura fold; production rho −0.05, fitted
  home advantage h=0.188069 on the seed fit).
- `harness.py` differs from GH's only in the sanctioned constants
  (data file, tournaments/counts, team keys by FotMob id,
  regular-phase-only eligibility, halves constant 0.4335, virgin
  tournaments, leg-(iii) threshold 4 of 7) — verified by diff.
- Dev re-run reproduces `results_dev.json` exactly; an independent
  second-path recomputation (fresh code fitting production
  `model_v2.DC` per fold, climatology and naive trailing-10
  reimplemented independently) reproduces every pooled metric to
  6 decimal places (max diff 3.8e-07) and the same gate outcome
  (LL ✓, RPS ✓, OU ✗).
- Dev predictions contain only the seven dev tournaments (1,630 rows
  = 815 × 2 arms); no 2025/2026 or 2026/2027 row was read (harness
  asserts the loaded seasons; `virgin()` raises `RuntimeError`
  before any virgin read — exercised and confirmed).
- Data builder re-run regenerates identical CSVs (1,448 rows, 1,326
  regular-phase, per-tournament counts as frozen in the prereg);
  EDA numbers re-run reproduces `eda_numbers.json` exactly.
- Environment note: during this build (2026-11-10 ~07:58–08:20 WIB)
  file writes from executed processes were blocked VM-wide
  (`PermissionError: [Errno 1] Operation not permitted` on every
  `write(2)` from Python, shell and git alike — the same failure
  that stopped the Codex implementation run mid-brief). The EDA
  JSONs were reconstructed through the agent file-write path and
  verified byte-exact against fresh script output; the engine was
  ported by the coordinator (Codex could not write) and verified
  against production as above. Writes recovered at ~08:21 WIB and
  all artifacts below were then generated by normal runs on disk.

## What ships

Nothing. No fitted params, no predictions, no daily-runner
activation. The confirmatory window 2026/2027 - Apertura stays
reserved and unread. League completion state: **complete** — the
only buildable candidate (G-SV) ran its full gate and failed; S/C/K/T
are not buildable (separate report).
