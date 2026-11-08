# Verdict — S-FI (FI-Veikkausliiga shots on target): **FAIL (virgin leg i)**

Frozen gates: PREREG_S_FI.md (1889033, before any fitting). Primary line 8.5,
ladder 7.5 / 8.5 / 9.5.

## Dev (warm-up 2021; scored 2022–2025, n = 678 stats rows)
Pooled LL@8.5: Gate Zero **0.683588**, RS **0.683698** vs league base rate
0.698133, naive trailing-10 0.693314 → **both arms pass the dev gate**.
(The base-rate baseline was recomputed independently from the league CSV —
0.698133, exact.)

## Virgin 2026 (n = 177) — read ONCE, for both dev-passing arms
| | LL@8.5 | calibration diff | SE |
|---|---|---|---|
| Gate Zero | 0.700940 | +2.02pp | 3.79pp |
| RS | 0.700602 | +2.06pp | 3.79pp |
| League base rate | 0.697801 | −11.00pp | |
| Naive trailing-10 | **0.691100** | −3.52pp | |

Leg (i): an arm's LL must be ≤ Gate Zero's AND ≤ the best baseline's.
RS beats Gate Zero (0.700602 ≤ 0.700940) but **both arms lose to the naive
baseline (0.691100)** → leg (i) FAILS for both arms. Leg (ii) would have
been PROVISIONAL for both (breach 2.02/2.06pp, within 1 SE of the 1pp
boundary), and RS's dev sign check passes (≤ GZ in 2 of 4 seasons) — all
moot under the mechanical reading. → **FAIL. Nothing ships.**

Independent verification: Gate Zero's virgin LL@8.5, calibration diff and
SE were recomputed from the harness's per-match virgin probabilities
against the league CSV — 0.700940 / +2.02pp / 3.79pp, exact.

## Defect found and removed (harness, not gates)
The inherited SOT harness's `choose()` falls back to "GZ" when no arm
passes, and its virgin-metrics run therefore wrote
`predictions/s_fi_virgin_predictions.csv` and
`engine/sot/fitted_params_virgin.json` for an arm that had NOT passed.
Both files were deleted before this verdict was committed; the numbers
above were recomputed from that CSV first (see verification), so the
deletion loses no evidence — `results_virgin.json` carries the full
record. The shipped predictions directory contains only the K-FI file.

Diagnosis (recorded, not acted on): the v5 pattern's dev edge over the
naive trailing-10 (0.6836 vs 0.6933) inverted on the virgin — 2026 was a
low-SOT season (8.70/match vs dev 8.72 pooled but with 2025's 9.46 spike
in the trailing state), and the model's ratings lagged the drop more
than the naive window did.
