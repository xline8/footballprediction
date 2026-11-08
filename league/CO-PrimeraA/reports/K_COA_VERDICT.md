# Verdict — K-COA (Colombia Primera A cards) — **FAIL** (dev gate; virgin NOT read)

Date: 2026-11-09. Branch `build/co-primeraa`. Prereg:
`league/CO-PrimeraA/prereg/PREREG_K_COA.md` (frozen in commit
3f57f1c before any fitting). Target: event-unified yellows, era
2023 - Apertura onward (stats-feed target rejected pre-fitting —
feed level break in 2022; card events absent 2021–2022). Arms:
Gate Zero (production cards pattern), X8 (referee multiplier,
J1 mechanics). Primary line 5.5. Dev: chronological online
walk-forward, seed 2023 - Apertura (n = 226), scored blocks
2023-Cl…2025-Cl (pooled n = 1,110).

## Dev results (coordinator-verified)

Pooled dev LL @5.5 (n = 1,110):

| arm | model | base rate | naive trailing-10 | dev gate |
|---|---|---|---|---|
| Gate Zero | 0.7001 | **0.6956** | 0.7080 | ✗ (loses to base) |
| X8 | **0.6918** | 0.6956 | 0.7080 | ✓ |

Gate Zero beats the naive baseline but **loses to the league base
rate** (0.7001 vs 0.6956) — the team-state model adds nothing over
the running league mean at this league's cards level. Per the
prereg's mechanical reading, Gate Zero failing its own dev gate
makes the variant moot: **verdict FAIL, virgin NOT read.**

## The X8 near-miss, recorded plainly

X8 passes the dev gate on its own numbers (0.6918 < both
baselines): the referee multiplier improves Gate Zero by −0.0083
LL — the trait measured in EDA (strictness r = 0.487, coverage
95.4% of dev-era rows) is real and pays. It still cannot ship:
the frozen program rule is that a variant is only ever read
against a Gate Zero that passed its own gate, and no rescue is
permitted inside the same prereg. A future, separately
pre-registered design could register the referee arm as the base
architecture for this league; that is a new prereg, NOT
authorised here, and the virgin (2026 - Apertura) remains unread
and available for it.

Context for the Gate Zero failure: this is a high-card league
(5.60 unified yellows/match) with weak defensive-side trait
reliability (yellows-against r = 0.289 on the era) — the decayed
team state has little to find beyond the league mean, and the
base rate is a strong opponent at the 5.5 line. The same
candidate family passed in PY (Gate Zero alone, line 4.5) and
failed in several other leagues; the gate is doing its job.

## Verification performed

- Coordinator re-ran `run_k_coa.py dev` from the committed code:
  output bit-identical to Codex's `results_dev.json`.
- `model.py` inspected: the X8 branch is the J1 mechanics verbatim
  (trailing referee yellows strictly before kickoff, K_REF = 8
  shrinkage toward the running league mean, multiplier clamped to
  [0.67, 1.50], <8 priors or unnamed referee → recorded fallback
  to Gate Zero); FB fallbacks are the seed block's measured means
  (2.642 / 3.013). State/Decayed core matches the PY port.
- Loader asserts the loaded season set equals exactly the six era
  tournaments in dev; the virgin path short-circuits before any
  2026 row is loaded (`results_virgin.json`: virgin_read = false).
- Referee coverage in the dev era: 1,275/1,336 = 95.4% (per
  tournament 91.2–98.7%) — the X8 adoption premise held; the arm
  failed only via the Gate Zero rule, not via coverage.

## Virgin

**Deliberately NOT read.** `engine/cards/results_virgin.json`
records `{"virgin_read": false, "verdict": "FAIL"}`.

## What ships

Nothing. No predictions CSV, no fitted params, no pipeline join.
K-COA verdict: **FAIL**.
