# Verdict — G-CO (Colombia Primera B goals) — **FAIL** (dev gate; virgin NOT read)

Date: 2026-11-09. Branch `build/co-primerab`. Prereg:
`league/CO-PrimeraB/prereg/PREREG_G_CO.md` (frozen in its own commit
4f88cff before any fitting). Arms: Gate Zero, SHRINK, X2 (Primera A
mover prior). Dev: season-blocked expanding walk-forward, seed 2021
(partial, n = 144 finished), evaluation seasons 2022–2024
(pooled n = 909).

## Dev results (coordinator-verified; see Verification)

Pooled dev (n = 909):

| arm | 1X2 LL | RPS | OU2.5 LL |
|---|---|---|---|
| Gate Zero | 1.0826 | 0.21816 | 0.7009 |
| SHRINK | **1.0579** | **0.21383** | 0.6870 |
| X2 | 1.0792 | 0.21712 | 0.6989 |
| climatology / base rate | 1.0639 | 0.21814 | **0.6710** |
| naive trailing-10 (reporting only) | 1.1450 | 0.21293 | 0.7588 |

Per season, model LL / OU LL (climatology LL / base OU LL):

| season | Gate Zero | SHRINK | X2 | climatology |
|---|---|---|---|---|
| 2022 (n=289) | 1.1756 / 0.7450 | 1.0978 / 0.7014 | 1.1756 / 0.7450 | 1.0771 / 0.6664 |
| 2023 (n=310) | 1.0509 / 0.6607 | 1.0509 / 0.6607 | 1.0394 / 0.6574 | 1.0691 / 0.6603 |
| 2024 (n=310) | 1.0276 / 0.7000 | 1.0276 / 0.7000 | 1.0291 / 0.6973 | 1.0465 / 0.6861 |

## Gate arithmetic (mechanical, prereg legs)

Dev gate — an arm must beat climatology on pooled 1X2 LL **and**
RPS, and beat the base rate on OU2.5 LL:

- **Gate Zero: LL 1.0826 > 1.0639 ✗; RPS 0.21816 > 0.21814 ✗ (by
  0.00002); OU 0.7009 > 0.6710 ✗ — fails all three legs.**
- SHRINK: LL ✓ (1.0579 < 1.0639), RPS ✓ (0.21383 < 0.21814),
  OU 0.6870 > 0.6710 ✗ — fails the OU leg.
- X2: LL 1.0792 > 1.0639 ✗, OU 0.6989 > 0.6710 ✗ — fails.

Per the prereg's mechanical reading, Gate Zero failing its own dev
gate makes the variants moot: **verdict FAIL, virgin NOT read**
(both variants also fail independently, so no reading of the rule
changes the outcome).

## Root causes, measured

1. **The partial 2021 seed poisons the 2022 evaluation.** Season
   2021 survives only as 144 finished matches (the Apertura regular
   season is placeholder files in the warehouse). Gate Zero's 2022
   LL (1.1756) is far worse than climatology (1.0771): clubs with
   thin recorded history get extreme ratings — Atletico Huila has
   3 prior in-league matches in the 2022 training window, Deportes
   Quindio 5. SHRINK repairs most of the damage (2022 LL 1.0978,
   a +0.078 gain from shrinking exactly those clubs) — the G-J2
   failure mode, confirmed live in this league — but not enough to
   beat climatology in 2022, and SHRINK is identical to Gate Zero
   in 2023–2024 (no 1–5-prior club in those windows).
2. **The OU leg fails in every dev season for every arm.** The
   totals level lags the league: this low-scoring league's OU2.5
   rate rose from .377 (2022) to .426 (2024) while prior-season
   fits price it off older, colder data — the same totals-
   calibration failure family as G-GE and G-BG2.
3. X2 works as designed where it bites — 2023 (the first mover
   season) improves to LL 1.0394 / OU 0.6574, the best model
   numbers of any arm-season — but it is identical to Gate Zero in
   2022 (no relegated arrivals) and slightly worse in 2024, so it
   cannot carry the pooled gate.

## Verification performed

- **Codex's chat summary of its own dev run did not match the
  results files it produced** (it reported pooled Gate Zero LL
  1.0268 / OU 0.6424; the files say 1.0826 / 0.7009). The
  coordinator re-ran `run_g_co.py dev` from the committed code:
  output bit-identical to the on-disk `results_dev.json`. The
  verdict rests on the re-run, file-based numbers only.
- Climatology pooled dev (LL 1.063931, RPS 0.218144, OU 0.671010)
  recomputed from the raw CSV through a second, independent script
  — exact match to the engine to 6 dp.
- `dc.py` diffed against the proven GE-Erovnuli reference:
  functionally identical (whitespace only).
- CSV audit: 1,639 finished rows, per-season counts and phase
  counts match the builder's independent warehouse audit; mover
  flags verified by team_id (2023: Cortulua, Patriotas; 2024:
  Union Magdalena, Atletico Huila); halves constant recomputed
  0.487518 ≈ frozen 0.4875; dev harness loads only 2021–2024
  (asserted in code), so 2025/2026 are unreachable in dev paths.

## Virgin

**Deliberately NOT read.** Per the frozen prereg: if Gate Zero
fails its dev gate, variants are moot, verdict FAIL, virgin NOT
read. Season 2025 (n = 308) remains untouched and available as a
virgin window for a future, separately pre-registered design
(a design that seeds on complete seasons only, or registers a
totals-level arm, would be the natural next attempt — NOT
authorised here). `engine/goals/results_virgin.json` records
`{"virgin_read": false, "reason": "gate zero failed dev gate"}`.

## What ships

Nothing. No predictions CSV, no fitted params, no pipeline join.
G-CO verdict: **FAIL**. The other four candidates (S/C/K/T) were
not buildable (no target data in any payload source for the
dev/virgin windows — see DATA_UNDERSTANDING / MODEL_DESIGN
feasibility matrix), so with the goals candidate through its gate,
**CO-PrimeraB is COMPLETE: 0 PASS / 1 FAIL, 4 markets not
buildable.**
