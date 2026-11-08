# Verdict — T-PY (PY-DivisionProfesional total shots)

**FAIL — all three arms passed the dev gate, read the transitional
virgin, and failed virgin leg (ii) calibration by a wide margin
(A and C also fail leg (i) vs naive). Nothing ships.**

Prereg: `league/PY-DivisionProfesional/prereg/PREREG_T_PY.md` (frozen
06d6a41, before any fitting). Engine: `engine/total_shots/` (KR/J1
shots-family port; coordinator verified the numbers below from the
results JSONs).

## Dev gate (pooled, 2025-Cl + 2026-Ap, n = 263 scored)

| arm | LL@24.5 |
|---|---|
| A (v1) | 0.6805 |
| B (v2 level layer) | 0.6803 |
| C (E9 trailing-r) | **0.6801** |
| league base rate | 0.6971 |
| naive trailing-10 | 0.6996 |

All arms beat both baselines ✓ → dev gate PASS for A, B, C.

## Virgin — 2026 - Clausura TRANSITIONAL (n = 112 played)

Actual over-rate at 24.5: **73.2%** (the virgin tournament is
shot-hot: mean 27.57 vs dev 24.83).

| arm | LL@24.5 | mean P(over) | calibration breach | SE |
|---|---|---|---|---|
| A | 0.6347 | 56.7% | **−16.55pp** | 4.18pp |
| B | 0.6169 | 59.5% | **−13.76pp** | 4.18pp |
| C | 0.6337 | 56.8% | **−16.40pp** | 4.18pp |
| naive trailing-10 | 0.6202 | 60.0% | −13.17pp | 4.22pp |

- Leg (i): B beats A and naive ✓; **A and C lose to naive ✗**.
- Leg (ii): every arm's breach (−13.8…−16.5pp) exceeds the frozen
  boundary 1.0pp + 1 SE ≈ 5.2pp by 8.6–11.4pp → **FAIL for all
  arms**, B included. No arm ships.

**Verification catch (recorded for the final audit; verdict-neutral):**
the virgin pass's `baseline_league` is degenerate (mean P(over) =
100%, LL 9.25 — its base-rate tracker misbehaves in the virgin
scoring pass; the dev pass's same baseline is sane, 0.6971). No leg
outcome depends on it: leg (ii) kills all three arms, and A/C also
lose leg (i) to the (sane) naive baseline. No virgin re-read was
made or is needed.

The season-end confirmatory read of the completed 2026 - Clausura
remains outstanding by design; it cannot change this verdict.
