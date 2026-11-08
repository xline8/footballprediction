# Verdict — G-PY (PY-DivisionProfesional goals)

**FAIL at the dev gate (OU2.5 leg). Virgin 2026 - Apertura NOT read.
Nothing ships.**

Prereg: `league/PY-DivisionProfesional/prereg/PREREG_G_PY.md` (frozen
in commit 06d6a41, before any fitting). Engine: `engine/goals/`
(BG-SecondLeague port; coordinator verified dc.py/arms.py/harness.py
against the BG reference and recomputed the pooled numbers below
independently from `engine/goals/results_dev.json`).

## Dev gate (pooled, 8 tournament blocks 2022-Ap…2025-Cl, n = 1,056)

| arm | 1X2 LL | RPS | OU2.5 LL |
|---|---|---|---|
| Gate Zero | **1.0536** | **0.2158** | 0.7035 |
| SHRINK | **1.0536** | **0.2158** | 0.7035 |
| climatology / base rate | 1.0956 | 0.2302 | **0.6875** |

Gate legs: 1X2 LL beats climatology ✓ · RPS beats climatology ✓ ·
**OU2.5 LL loses to the base rate (0.7035 vs 0.6875) ✗** → both arms
dead at the dev gate. The familiar program shape (G-J2/G-NL/G-AU):
the DC 1X2 structure is honest, the totals leg is not — Paraguay's
tournament O2.5 rate swings 38.6%–51.5% and the decayed fit chases
it late.

**SHRINK degeneracy, recorded plainly:** SHRINK's numbers are
identical to Gate Zero's in every block row. Not a port bug (arms.py
is a faithful BG port, diffed): under tournament-blocked fitting,
every team's prior in-league match count at a block fit is either 0
(where SHRINK ≡ Gate Zero's unseen rule) or ≥ 18 (n/6 factor = 1).
Verified directly from the CSV for every dev block — no team ever
sits at 1–17 prior matches. The sanctioned arm cannot bite under
this block structure; the OU leg kills both arms identically.

## Virgin

**Deliberately NOT read** (frozen rule: Gate Zero fails its dev gate
⇒ FAIL, virgin unburned). 2026 - Apertura remains available for one
future read under a new prereg; 2026 - Clausura stays reserved as
the confirmatory window.
