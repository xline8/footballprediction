# C-SE verdict — PROVISIONAL PASS (arm X7 ships)

Prereg: `league/SE-Allsvenskan/prereg/PREREG_C_SE.md` (frozen in
commit 62320f5, before any fitting). Primary line 10.5. Dev =
walk-forward evaluation seasons 2022–2024 (pooled n = 720);
virgin = 2025 (n = 240), read once.

## Dev results (pooled LL@10.5)

| Arm / baseline | LL@10.5 |
|---|---|
| Gate Zero (X9) | 0.6966 |
| X7 (box touches) | 0.6910 |
| League base rate | 0.7314 |
| Naive trailing-10 | 0.7267 |

Both arms beat both baselines. X7's per-season sign check vs Gate
Zero is 3/3 (2022: 0.6909 < 0.6954; 2023: 0.6913 < 0.7034; 2024:
equal at 0.6910).

## Virgin results (2025, n = 240; actual over-10.5 rate 0.5375)

| Arm | LL@10.5 | Calibration | SE | Fitted beta |
|---|---|---|---|---|
| Gate Zero | 0.7027 | −3.12pp | 3.26pp | poss 0.0025, bc 0.0 |
| X7 | 0.6940 | −3.11pp | 3.23pp | box-touch 0.0 |
| League base rate | 0.7486 | | | |
| Naive trailing-10 | 0.7487 | | | |

## Gate arithmetic

- Dev gate: both arms pass (above).
- Virgin leg (i): X7 0.6940 ≤ Gate Zero 0.7027 ✓ and ≤ best
  baseline 0.7486 ✓; Gate Zero also ≤ best baseline ✓.
- Virgin leg (ii): both arms breach 1.0pp (−3.12 / −3.11pp) but
  within 1 SE of the boundary (limits 4.26 / 4.23pp) →
  **PROVISIONAL PASS** for both.
- Leg (iii): X7 3/3 ✓.
- Both-pass rule: lower pooled virgin LL ships → **X7**.

## Honest mechanism note

X7's fitted box-touch beta is **0.0 in every dev season and in the
virgin fit** — the territorial multiplier is inert, exactly the J1
outcome. X7 wins not because opp-box touches add signal inside
this architecture, but because its no-multiplier form beats Gate
Zero's small fitted possession beta (0.0025). The gate, not the
story, decides: the arm as pre-registered passes and ships.

**Verdict: PROVISIONAL PASS. Arm X7 ships.** Predictions:
`predictions/c_se_virgin_predictions.csv` (240 rows; FT ladder
9.5/10.5/11.5; 1H/2H presentation-only via the frozen corners
constant 0.473). Fitted params:
`engine/corners/fitted_params_virgin.json` (gamma 0.15, NB r ≈
1.196, beta [0.0]). Predictions-only product.
