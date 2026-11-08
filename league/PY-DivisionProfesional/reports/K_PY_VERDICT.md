# Verdict — K-PY (PY-DivisionProfesional cards)

**FAIL — Gate Zero passed the dev gate, read the transitional
virgin, and failed virgin leg (i). Nothing ships.**

Prereg: `league/PY-DivisionProfesional/prereg/PREREG_K_PY.md` (frozen
06d6a41, before any fitting). Target = **event-unified yellows**
(decision + dev-era feed evidence in analysis/DATA_UNDERSTANDING.md,
taken before fitting). Single arm by design (X8 dropped pre-fitting:
dev-era referee coverage 11.1%). Engine: `engine/cards/` (KR port,
target columns repointed to `ev_yellow_inc2nd_*`; coordinator
recomputed the pooled dev numbers independently from
`engine/cards/results_dev.json`).

## Dev gate (pooled, 2025-Cl + 2026-Ap, n = 263 scored)

| arm | LL@4.5 |
|---|---|
| Gate Zero | **0.6795** |
| league base rate | 0.6852 |
| naive trailing-10 | 0.6834 |

Beats both baselines ✓ → dev gate PASS, virgin read authorised.

## Virgin — 2026 - Clausura TRANSITIONAL (n = 112 played)

| arm | LL@4.5 | mean P(over 4.5) | actual over-rate |
|---|---|---|---|
| Gate Zero | 0.7195 | 0.4872 | 0.4643 |
| league base rate | **0.6992** | 0.4935 | 0.4643 |
| naive trailing-10 | **0.7112** | 0.3923 | 0.4643 |

- Leg (i) LL: 0.7195 ≤ base rate 0.6992? **No — FAIL** (also loses
  to naive 0.7112). The virgin tournament ran cold on cards
  (event-unified mean ≈ 4.18 vs dev 4.89) and the model's dispersion
  fit (r = 110, near-Poisson on the virgin fit window) priced the
  4.5 line worse than a flat base rate.
- Leg (ii) calibration: breach **+2.29pp**, SE 4.86pp → beyond the
  1.0pp clean boundary but within 1 SE → would have been
  PROVISIONAL PASS. Moot: leg (i) already failed.

Verdict FAIL by the frozen legs. The season-end confirmatory read
of the completed 2026 - Clausura remains outstanding by design; it
cannot change this verdict.
