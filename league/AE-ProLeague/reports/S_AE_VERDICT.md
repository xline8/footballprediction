# Verdict — S-AE (AE-ProLeague shots on target)

**FAIL at virgin leg (ii) calibration (both arms).** Nothing ships.
Virgin read once, for both dev-passing arms.

Dev LL@9.5 (n=545, recomputed exactly): Gate Zero 0.692764, RS
0.691859; baselines: league base rate 0.701265, naive trailing-10
0.700856. Both arms pass the dev gate; RS sign check 3/3.

Virgin 2025/2026 (n=182, recomputed exactly from
`engine/sot/predictions_virgin.csv`):

| Arm | LL@9.5 | Mean P(over) | Actual over | Breach (pred − actual) | 1 SE | Leg (i) | Leg (ii) |
|---|---|---|---|---|---|---|---|
| Gate Zero | 0.634819 | 0.3499 | 0.2967 | **+5.32pp** | 3.47pp | PASS (≤ base 0.639857, ≤ naive 0.646833) | **FAIL** (5.32 > 1 + 3.47) |
| RS | 0.634091 | 0.3491 | 0.2967 | **+5.24pp** | 3.47pp | PASS | **FAIL** |

The virgin season ran cold on SOT (8.18/match vs 9.06–9.61 in the dev
folds — the EDA-flagged level drop): both arms keep predicting the dev
level and overstate the over-rate by >5pp, beyond the provisional band.
LL still beat both baselines; calibration is the leg that kills it.
