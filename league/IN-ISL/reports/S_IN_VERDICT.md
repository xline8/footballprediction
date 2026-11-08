# Verdict — S-IN (India Indian Super League shots on target)

**PASS (PROVISIONAL, calibration) — Gate Zero SHIPS.**
Primary line 8.5. Virgin predictions:
`predictions/s_in_virgin_predictions.csv` (Gate Zero, n=91).

## Dev (walk-forward, scored 2022/2023–2024/2025, n=419; pooled LL@8.5)

| Arm / baseline | LL@8.5 |
|---|---|
| Gate Zero | 0.6851 |
| RS | 0.6848 |
| X4 | 0.6889 |
| League base rate | 0.6918 |
| Naive trailing-10 | 0.6979 |

All three arms beat both baselines → all three read the virgin.

## Virgin (2025/2026, n=91; read ONCE)

| Arm / baseline | LL@8.5 | Calibration (mean P − actual) | SE |
|---|---|---|---|
| Gate Zero | 0.6721 | +3.60pp | 5.14pp |
| RS | 0.6706 | +3.54pp | 5.14pp |
| X4 | 0.6748 | +2.83pp | 5.16pp |
| League base rate | 0.6811 | +8.54pp | — |
| Naive trailing-10 | 0.6729 | +1.68pp | — |

## Gate arithmetic (frozen legs, applied mechanically)

- **Gate Zero**: leg (i) 0.6721 ≤ best baseline 0.6729 ✓ (and ≤
  Gate Zero trivially); leg (ii) |+3.60pp| > 1pp clean band, but
  the breach beyond the band (2.60pp) is within 1 SE (5.14pp) →
  **PROVISIONAL PASS**. The virgin ran cold on SOT (7.79/match vs
  dev 8.49); at n=91 the SE is wide and the provisional band is
  doing exactly the work it was frozen for.
- **RS**: best virgin LL (0.6706) and provisional calibration,
  but leg (iii) — the dev per-season sign check — is **1/3**
  (2022/2023: 0.6716 > GZ 0.6713; 2023/2024: 0.6845 > 0.6831;
  2024/2025: 0.6944 < 0.6966). A variant must win ≥2 of 3 →
  RS fails as written, despite the better virgin number.
- **X4**: leg (i) fails (0.6748 > Gate Zero 0.6721) and its sign
  check is 0/3. Out.
- Both-pass rule therefore resolves to Gate Zero alone.

Independent verification: LL@8.5 and the calibration diff were
recomputed from the shipped predictions CSV by a second path —
0.6721 and +3.60pp, exact. The dev league base rate was likewise
recomputed by hand from the raw CSV (0.6918, exact).

## What ships

Gate Zero (unmodified v5 pattern), fitted params in
`engine/sot/fitted_params_virgin.json`. FT ladder 7.5/8.5/9.5;
1H/2H presentation-only via the frozen SOT constant 0.453.
X6 was never built (FEATURES dropped it: xGOT era = one dev
season, trait r≈0.35).
