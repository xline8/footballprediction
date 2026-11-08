# Verdict — G-COA (Colombia Primera A goals) — **FAIL** (dev gate; virgin NOT read)

Date: 2026-11-09. Branch `build/co-primeraa`. Prereg:
`league/CO-PrimeraA/prereg/PREREG_G_COA.md` (frozen in its own
commit 3f57f1c before any fitting). Arms: Gate Zero, X2 (Primera B
mover prior: a = ln 0.81, d = ln 1.18). Dev: tournament-blocked
expanding walk-forward, seed 2021-Ap+Cl (n = 411), evaluation
2022-Ap…2025-Cl (pooled n = 1,788).

## Dev results (coordinator-verified; see Verification)

Pooled dev (n = 1,788):

| arm | 1X2 LL | RPS | OU2.5 LL |
|---|---|---|---|
| Gate Zero | 1.0367 | 0.20810 | 0.6842 |
| X2 | **1.0312** | **0.20653** | 0.6813 |
| climatology / base rate | 1.0592 | 0.21588 | **0.6714** |
| naive trailing-10 (reporting only) | 1.0899 | 0.22176 | 0.7468 |

Per tournament, model 1X2 LL (Gate Zero / X2; climatology LL):

| tournament | Gate Zero | X2 | climatology |
|---|---|---|---|
| 2022 - Apertura | 1.0417 | 1.0250 | 1.0503 |
| 2022 - Clausura | 1.1105 | 1.0830 | 1.0705 |
| 2023 - Apertura | 1.0256 | 1.0328 | 1.0384 |
| 2023 - Clausura | 1.0108 | 1.0051 | 1.0448 |
| 2024 - Apertura | 1.0677 | 1.0682 | 1.0822 |
| 2024 - Clausura | 1.0017 | 1.0030 | 1.0568 |
| 2025 - Apertura | 1.0195 | 1.0164 | 1.0703 |
| 2025 - Clausura | 1.0160 | 1.0160 | 1.0609 |

## Gate arithmetic (mechanical, prereg legs)

Dev gate — an arm must beat climatology on pooled 1X2 LL **and**
RPS, and beat the base rate on OU2.5 LL:

- **Gate Zero: LL 1.0367 < 1.0592 ✓; RPS 0.20810 < 0.21588 ✓;
  OU 0.6842 > 0.6714 ✗ — fails the OU leg.**
- X2: LL ✓ (1.0312), RPS ✓ (0.20653), OU 0.6813 > 0.6714 ✗ —
  fails the same leg independently.

Per the prereg's mechanical reading, Gate Zero failing its own dev
gate makes the variant moot: **verdict FAIL, virgin NOT read**
(X2 also fails independently, so no reading of the rule changes
the outcome).

## Root cause, measured

The 1X2 side is genuinely good — both arms beat climatology on LL
in 8 of 9 tournaments and on RPS pooled by a wide margin. The OU
leg fails in 8 of 9 tournaments for both arms: the model's totals
level lags the league. Dev OU2.5 rates rose across the window
(0.38 in most blocks, 0.469 in 2025-Cl) while decayed fits price
totals off older, colder data — the same totals-calibration
failure family as G-CO (Primera B), G-GE and G-BG2. X2 works where
it bites (2022 blocks: LL −0.017/−0.027 vs Gate Zero — the promoted
clubs' openers priced correctly) but a mover prior cannot repair a
league-wide totals level.

## Verification performed

- Coordinator re-ran `run_g_coa.py dev` from the committed code:
  output bit-identical to the on-disk `results_dev.json` produced
  by Codex.
- Climatology pooled dev (LL 1.059172, RPS 0.215877, OU 0.671363)
  recomputed from the raw CSV through a second, independent script
  — exact match to 6 dp.
- `dc.py` diffed against the proven CO-PrimeraB reference:
  identical. `arms.py` inspected: X2 replaces ratings with exactly
  ln(0.81)/ln(1.18) for mover_up clubs, nothing else.
- Dev harness loads only seed+dev seasons (asserted in code);
  virgin path asserts 2026 - Clausura is absent and was never
  reached (dev gate short-circuit).

## Virgin

**Deliberately NOT read.** Per the frozen prereg: if Gate Zero
fails its dev gate, variants are moot, verdict FAIL, virgin NOT
read. Season 2026 - Apertura (n = 204) remains untouched as a
virgin window for a future, separately pre-registered design (a
totals-level arm would be the natural next attempt — NOT
authorised here). `engine/goals/results_virgin.json` records
`{"virgin_read": false, "verdict": "FAIL"}`.

## What ships

Nothing. No predictions CSV, no fitted params, no pipeline join.
G-COA verdict: **FAIL**.
