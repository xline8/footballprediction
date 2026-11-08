# Verdict — C-PY (PY-DivisionProfesional corners)

**FAIL — Gate Zero failed the dev gate; under the frozen rule the
variant is moot and the virgin was NOT read. Nothing ships.**

Prereg: `league/PY-DivisionProfesional/prereg/PREREG_C_PY.md` (frozen
06d6a41, before any fitting). Engine: `engine/corners/` (KR/J1 port;
coordinator recomputed the pooled numbers below independently from
`engine/corners/results_dev.json`).

## Dev gate (pooled, 2025-Cl + 2026-Ap, n = 263 scored)

| arm | LL@8.5 |
|---|---|
| Gate Zero | 0.7211 |
| X7 | **0.6918** |
| league base rate | 0.7313 |
| naive trailing-10 | **0.7180** |

Gate legs (arm must beat BOTH baselines): Gate Zero beats the base
rate ✓ but **loses to naive trailing-10 (0.7211 vs 0.7180) ✗** →
Gate Zero is dead. X7 beat both baselines clearly (0.6918 vs 0.7313 /
0.7180) and would have gone to the virgin — but the prereg's
mechanical reading, frozen before fitting, is explicit: *"If Gate
Zero fails its own dev gate, variants are moot, verdict FAIL, virgin
NOT read."* The rule was applied as written (the K-TR incident is
what happens when it is not). X7's dev strength is recorded here as
the honest signal for a possible future prereg with a fresh virgin.

Per-block model LL@8.5: 2025-Cl GZ 0.7523 / X7 0.6965; 2026-Ap GZ
0.6896 / X7 0.6870 — X7 better in both blocks (its touches
multiplier is active and non-degenerate in this league, unlike the
β = 0 pattern seen elsewhere).

## Virgin

**Deliberately NOT read.** 2026 - Clausura (transitional, n = 112)
remains unburned for the count markets' shared window discipline;
a future C-PY prereg (e.g. with the completed 2026-Clausura as
virgin and X7 as a named arm) is a coordinator/user decision, not
taken here.
