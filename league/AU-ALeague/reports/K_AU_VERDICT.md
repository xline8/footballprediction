# K-AU verdict — PASS (calibration PROVISIONAL) — Gate Zero SHIPS

Prereg: `prereg/PREREG_K_AU.md` (frozen b353f24, before fitting).
Primary line 3.5. Dev pooled n = 508; virgin 2025/2026 n = 163,
read once. K-AU is Gate-Zero-only by preregistered design: the
X8 referee arm was NOT built because FEATURES dropped X8 on
both adoption legs (referee strictness split-half r = 0.06 in
AU — noise, vs J1 0.646 / DK 0.561 — and referee coverage only
82.8% in the virgin season). The engine's referee fields are
inert remnants of the reference harness (multiplier 1.0,
`fallback_reason = gate_zero_only` on every row); no referee
covariate exists in the model.

## Dev results — pooled LL@3.5

| Arm / baseline | LL@3.5 |
|---|---|
| Gate Zero | 0.6857 |
| League base rate | 0.6887 |
| Naive trailing-10 | 0.6958 |

Gate Zero beats both baselines → passes the dev gate (by
0.0029 over the base rate — the thinnest dev margin of AU's
four read candidates; recorded, not rounded up).

## Virgin results (2025/2026, n = 163)

| Arm / baseline | LL@3.5 | Calibration |
|---|---|---|
| Gate Zero | 0.6855 | −4.07pp (SE 3.89pp) |
| League base rate | 0.6969 | — |
| Naive trailing-10 | 0.6921 | — |

## Gate arithmetic

- Leg (i): 0.6855 ≤ best baseline 0.6921 — PASS.
- Leg (ii): |−4.07pp| breaches the 1.0pp boundary by 3.07pp,
  which is within 1 SE (3.89pp) → **PROVISIONAL PASS**. The
  virgin season's over-3.5 rate (50.9%) ran well above the
  model's mean prediction (46.9%) — AU yellows recovered in
  2025/2026 (3.61/match) after the dev-era step-down, and the
  HL-270 ratings lagged it, the same level-shift mechanism as
  K-DK/K-J2, here absorbed by the provisional band instead of
  failing.
- No variant arms exist; the both-pass rule reduces to
  Gate Zero passing, which it does.

**Ships:** Gate Zero (production cards pattern), fitted
parameters in `engine/cards/fitted_params_virgin.json`, virgin
predictions in `predictions/k_au_virgin_predictions.csv`
(163 rows; FT ladder 2.5/3.5/4.5; 1H/2H presentation via the
frozen yellows constant 0.308). **AU joins the daily runner
with cards.** Note: the harness's NB size estimate hit its
500 cap for model/base/naive on the virgin fit (near-Poisson
yellows, dispersion 0.90); the gate outcome does not turn on
it. Coordinator verification: K virgin numbers cross-checked
against `results_virgin.json`; prediction halves regenerated
with the AU constant after a DK-constant leak (0.319) was
caught in verification and fixed before commit.
