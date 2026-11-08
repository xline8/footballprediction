# Verdict — G-WAL (Wales Cymru Premier goals model)

**FAIL at the dev gate. Nothing ships. Virgin 2025/2026 deliberately NOT read.**

Prereg `league/WAL-CymruPremier/prereg/PREREG_G_WAL.md` (commit
`50f8e34a`) precedes all fitting. Branch `build/wal-cymru-premier`.
Engine `league/WAL-CymruPremier/engine/goals/`; dev results
`results_dev.json` (+ CSV, `predictions_dev.csv`).

## Dev results (season-blocked expanding walk-forward, n=576)

| arm | season | kind | n | 1X2 LL | RPS | OU2.5 LL |
|---|---|---|---:|---:|---:|---:|
| Gate Zero | 2022/2023 | model | 192 | 0.979587 | 0.213985 | 0.729806 |
| Gate Zero | 2022/2023 | climatology | 192 | 1.037495 | 0.237671 | 0.693147 |
| Gate Zero | 2022/2023 | naive trailing-10 | 192 | 1.318033 | 0.277480 | 0.795822 |
| Gate Zero | 2023/2024 | model | 192 | 0.913119 | 0.183892 | 0.725218 |
| Gate Zero | 2023/2024 | climatology | 192 | 1.071184 | 0.237847 | 0.688801 |
| Gate Zero | 2023/2024 | naive trailing-10 | 192 | 1.098787 | 0.244403 | 0.724571 |
| Gate Zero | 2024/2025 | model | 192 | 1.047772 | 0.235084 | 0.662261 |
| Gate Zero | 2024/2025 | climatology | 192 | 1.051237 | 0.237267 | 0.678799 |
| Gate Zero | 2024/2025 | naive trailing-10 | 192 | 1.104703 | 0.240291 | 0.729500 |
| **Gate Zero** | **pooled** | **model** | **576** | **0.980160** | **0.210987** | **0.705762** |
| **Gate Zero** | **pooled** | **climatology** | **576** | **1.053306** | **0.237595** | **0.686916** |
| **Gate Zero** | **pooled** | **naive trailing-10** | **576** | **1.173841** | **0.254058** | **0.749964** |
| SHRINK | 2022/2023 | model | 192 | 0.979587 | 0.213985 | 0.729806 |
| SHRINK | 2023/2024 | model | 192 | 0.913119 | 0.183892 | 0.725218 |
| SHRINK | 2024/2025 | model | 192 | 1.047772 | 0.235084 | 0.662261 |
| **SHRINK** | **pooled** | **model** | **576** | **0.980160** | **0.210987** | **0.705762** |

SHRINK is identical to Gate Zero in every fold (changed_rows = 0,
target_teams_1_5 = 0 in all three folds) — the structural no-op the
prereg predicted: no team in any dev fold has 1–5 prior in-league
matches, so the arm cannot bite. Its climatology/naive rows are
identical to Gate Zero's and are omitted above for brevity; the full
24 rows are in `results_dev.csv`.

## Gate arithmetic (mechanical, per prereg)

Dev gate — pooled model must beat climatology on 1X2 LL and RPS, and
beat the base rate on OU2.5 LL:

- 1X2 LL: 0.980160 vs 1.053306 — model **wins by −0.073146** ✓
- RPS: 0.210987 vs 0.237595 — model **wins by −0.026608** ✓
- OU2.5 LL: 0.705762 vs 0.686916 — model **loses by +0.018846** ✗

Gate Zero fails one of the three legs (the OU2.5 leg), so Gate Zero
fails its dev gate. Per the frozen rule in the prereg ("If Gate Zero
fails its own dev gate, variants are moot, verdict FAIL, virgin NOT
read" — enforced mechanically by the harness: `virgin()` raises
`RuntimeError` unless Gate Zero passed dev, verified by the
coordinator), **no virgin leg is evaluated and the virgin window stays
unread** — no `results_virgin.json` from a read, no
`fitted_params_virgin.json`, no virgin predictions file, and no
`league/WAL-CymruPremier/predictions/` directory exists. The marker
`engine/goals/results_virgin.json` records `{"virgin_read": false}`
so the not-read state is on record in the tree.

## The SHRINK fork (recorded plainly, not acted on)

SHRINK's numbers are Gate Zero's numbers exactly (the arm is a
structural no-op here), so it fails the same OU2.5 leg by the same
+0.018846 and passes the same two legs. It does NOT proceed to the
virgin window, because the frozen prereg makes Gate Zero's dev pass a
precondition for any virgin read. The numbers are recorded here in
full so the coordinator can judge whether the "variants are moot"
rule should ever be revisited; this build does not revisit it.

Fold reading: Gate Zero beats climatology on 1X2 LL and RPS in all
three folds, and beats the naive trailing-10 on LL and RPS pooled
(LL 0.980 vs 1.174; RPS 0.211 vs 0.254) — but on OU2.5 it loses to
the base rate in two of three folds (2022/2023: 0.730 vs 0.693;
2023/2024: 0.725 vs 0.689) and wins only in 2024/2025 (0.662 vs
0.679). The 2024/2025 fold is also the weakest 1X2 fold (model LL
1.0478 vs climatology 1.0512 — a win by only −0.0035). The naive
baseline is notably poor in 2022/2023 (LL 1.318 vs climatology
1.037): with one season of history, trailing-10 ratings for the two
promoted clubs fall back to the league mean and the fold's high home-win
rate (50.5%) punishes the naive. The naive numbers were reproduced
exactly by an independent recomputation, so the baseline is faithful —
it is simply a bad baseline in this league. The gate does not depend on
it.

## Independent verification (coordinator, not Codex)

- Pooled and per-fold model LL/RPS/OU2.5 LL recomputed from
  `predictions_dev.csv` by a fresh script: identical to
  `results_dev.json` to 6 decimals for both arms, all folds.
- Climatology per-fold and pooled recomputed from `wal_matches.csv`:
  identical to 6 decimals.
- Naive trailing-10 recomputed from scratch: identical to 6 decimals.
- `dc.py` diffed against TZ's: only the module docstring differs.
- `virgin()` invoked once to test the gate: raised `RuntimeError`
  ("Gate Zero failed the dev gate; virgin evaluation is prohibited")
  before loading any virgin row.

## Verdict

G-WAL is **FAIL**. Nothing ships. The 2025/2026 virgin window was
**NOT READ**; the 2026/2027 confirmatory window remains reserved.
Production code untouched. No push. No merge.
