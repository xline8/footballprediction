# Verdict — G-GE (GE-Erovnuli goals) — **FAIL** (dev gate; virgin NOT read)

Date: 2026-11-09. Branch `build/ge-erovnuli`. Prereg:
`league/GE-Erovnuli/prereg/PREREG_G_GE.md` (frozen in its own commit
before any fitting). Arms: Gate Zero, SHRINK. Dev: season-blocked
expanding walk-forward, evaluation seasons 2022–2024 (pooled n=540).

## Dev results (verified independently by the coordinator)

| arm | 1X2 LL | RPS | OU2.5 LL |
|---|---|---|---|
| Gate Zero | 1.0139 | 0.2074 | 0.7313 |
| SHRINK | 1.0139 | 0.2074 | 0.7313 |
| climatology / base rate | 1.0771 | 0.2306 | **0.6977** |

Per season (Gate Zero OU2.5 LL vs base rate): 2022 0.6951 vs 0.6969
(model better); 2023 0.7648 vs 0.6991; 2024 0.7339 vs 0.6972.

## Gate arithmetic (mechanical, prereg legs)

- 1X2 LL leg: 1.0139 < 1.0771 ✓. RPS leg: 0.2074 < 0.2306 ✓.
- **OU2.5 LL leg: 0.7313 > 0.6977 ✗ — the arm must beat the base-rate
  baseline; it does not. Both arms are dead at the dev gate.**

Root cause, measured: the fit systematically lags the league's goal
level (mean predicted λ-total 2.46 for 2022 vs actual 2.74; 2.46 for
2023 vs actual 3.15) and 2023 was a regime-jump season (3.15 gpm,
OU2.5 rate .628 vs .467–.511 in the training seasons) that no
prior-season fit could foresee. The 1X2/RPS legs pass comfortably —
the ratings carry real signal (EDA F2) — but the totals calibration
the OU leg demands is not there on dev.

## SHRINK degeneracy (construction fact, reported not repaired)

SHRINK is numerically identical to Gate Zero on every dev match:
under season-blocked fitting every evaluated team has either 0 prior
in-league matches (n=0 ⇒ factor 0, identical to Gate Zero's unseen
rule) or ≥36. The 1–5-match window the arm targets never occurs.
This is the degeneracy the IN-ISL prereg recorded in advance as a
possibility; per discipline it is reported, not repaired mid-flight.

## Verification performed

- Engine diffed against the J1 reference: lambda construction,
  sweeps, rho grid identical (goals-only per prereg).
- Climatology pooled OU LL recomputed through a second path:
  0.697709 — matches the engine to 6 dp.
- Per-season predicted-vs-actual totals recomputed from the engine's
  own fit path (numbers in the root-cause paragraph above).

## Virgin

**Deliberately NOT read.** Per the frozen prereg: if Gate Zero fails
its dev gate, variants are moot, verdict FAIL, virgin NOT read.
Season 2025 remains untouched and available as a virgin window for a
future, separately pre-registered design.

## What ships

Nothing. No predictions CSV, no fitted params, no pipeline join.
G-GE verdict: **FAIL**. The other four candidates (S/C/K/T) were not
buildable (no target data in any payload source — see
DATA_UNDERSTANDING / MODEL_DESIGN feasibility matrix), so with the
goals candidate through its gate, **GE-Erovnuli is COMPLETE**.
