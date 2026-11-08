# Verdict — G-SAFD (goals): **FAIL**

Prereg: `prereg/PREREG_G_SAFD.md` (frozen before fitting). The dev harness
used only 2024/2025 regular, non-awarded matches: warm-up 90 and scored
n = 216. Gate Zero fails the preregistered dev gate on the OU2.5 leg, so the
virgin season was deliberately unread and nothing ships.

## Dev (within-season walk-forward; pooled scored block)

| Arm | 1X2 LL | RPS | OU2.5 LL |
|---|---:|---:|---:|
| Gate Zero | 1.034624 | 0.208573 | 0.722447 |
| SHRINK | 1.034624 | 0.208573 | 0.722447 |
| Climatology | 1.095570 | 0.229875 | 0.696270 |

## Gate arithmetic

The dev gate requires pooled 1X2 LL and RPS to beat climatology, and OU2.5
LL to beat the base-rate baseline. Gate Zero passes the first two legs:

- 1X2 LL: 1.034624 < 1.095570
- RPS: 0.208573 < 0.229875
- OU2.5 LL: 0.722447 > 0.696270 — **FAIL**

Gate Zero therefore fails its own dev gate. Under the frozen mechanical
reading, SHRINK is moot, the virgin is **not read**, and the verdict is FAIL.

The virgin legs were consequently not evaluated: (i) virgin 1X2 LL versus
Gate Zero and climatology; (ii) home-win and OU2.5 calibration using
actual − predicted, with breaches reported in percentage points and SEs;
and (iii) the variant sign check against Gate Zero's pooled dev 1X2 LL.
The both-pass rule and simpler-arm tie rule are not reached.

## What ships

**Nothing ships.** No virgin prediction CSV was produced because no arm
reached the virgin evaluation stage.

## Verification notes

- `safd_matches.csv` contains 306 eligible 2024/2025 regular matches and
  304 eligible 2025/2026 regular matches after filtering `phase == regular`
  and `awarded == 0`.
- The engine asserts dev scored n = 216 and never loads 2026/2027 rows.
- Both arms use the same fixed Dixon–Coles math, rho grid, 270-day decay,
  and date-grouped expanding fits; SHRINK has no scored impact in this dev
  block, producing identical pooled metrics.
- Virgin state is explicit in `results_virgin.json`:
  `{"virgin_read": false, "reason": "Gate Zero failed dev gate"}`.
- `fitted_params_virgin.json` in the engine folder is an unfitted-DC
  stub written by the harness on the refused-virgin path (rho 0.0,
  training_rows 0, empty ratings) — it contains NO fitted virgin
  parameters, because the virgin was never fit. Do not mistake it
  for a fitted parameter set.
- Independent verification (coordinator, 2026-11-10): dev pooled
  numbers recomputed from `predictions_dev.csv` (432 rows, both arms)
  match `results_dev.json` exactly (LL 1.034624 / RPS 0.208573 /
  OU 0.722447; climatology 1.095570 / 0.229875 / 0.696270); the league
  DC port was replayed against production `model_v2.DC` on the first
  scored date (2024-11-25) with max probability difference 0.000000;
  the harness's date-grouped expanding fits, season filter
  (regular + awarded 0) and calibration rule were read and confirmed.
