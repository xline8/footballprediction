# Verdict — C-IE (Ireland Premier Division corners) — **PROVISIONAL PASS** (Gate Zero ships)

Prereg: `prereg/PREREG_C_IE.md`. Primary line 9.5. Arms: Gate Zero
(X9: possession + big-chance multiplier) and X7 (box-touch
multiplier).

## Dev (walk-forward, warm-up 2022, scored 2023–2025, n = 540)

| | LL@9.5 |
|---|---|
| X7 | **0.6941** |
| Gate Zero | 0.7039 |
| Naive trailing-10 | 0.7193 |
| League base rate | 0.7276 |

Both arms pass the dev gate. X7's per-season sign check vs Gate
Zero: 2023 better (0.6956 vs 0.7396), 2024 worse (0.6943 vs
0.6872), 2025 worse (0.6923 vs 0.6848) — 1 of 3.

## Virgin (2026, n = 180, read ONCE for both dev-passing arms)

| | LL@9.5 | calib diff (SE) |
|---|---|---|
| Gate Zero | **0.6817** | −1.32pp (3.69) |
| X7 | 0.7108 | −1.41pp (3.78) |
| League base rate | 0.7557 | — |
| Naive trailing-10 | 0.7500 | — |

(Independently recomputed from the predictions CSV: Gate Zero LL
0.6817, diff −0.0132, SE 0.0369 — exact.)

- Gate Zero: leg (i) PASS (0.6817 ≤ best baseline 0.7500);
  leg (ii): |−1.32pp| breaches the 1.0pp clean boundary but lies
  within 1 SE of it (band = 1.0 + 3.69 = 4.69pp) →
  **PROVISIONAL PASS**.
- X7: leg (i) FAIL (0.7108 > Gate Zero 0.6817) and leg (iii) FAIL
  (sign check 1 of 3). Dead despite the better dev LL — the
  box-touch multiplier (partial coverage before 2024) did not
  transfer to the virgin season.

**Ships: Gate Zero, PROVISIONAL.** Fitted virgin params
(`engine/corners/fitted_params_virgin.json`): gamma 0.3,
NB r = 1.2195, beta = [0.0 (possession), 0.025 (big chance)],
fit_n = 707. Predictions:
`predictions/c_ie_virgin_predictions.csv` (FT ladder 8.5/9.5/10.5;
1H/2H presentation-only via the frozen corners constant 0.4762).
