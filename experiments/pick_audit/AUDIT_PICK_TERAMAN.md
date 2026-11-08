# Pick Teraman audit

Window: 2026-10-29 through 2026-11-08. The ledger subset is
`product == "pick_teraman"`, `level == "leg"`, with `status` equal to
`hit` or `lose`. Its predicted probability is the ledger `p_model`; the
ledger identifies tiers as `best` and `fallback`.

The archive's `market_compare.csv` files contain odds and `p_implied`, but no
model-probability column. The audit joins each row to that day's archived
prediction snapshot and derives the market probability from `ph_dc`, `pd_dc`,
`pa_dc`, the stored over/under fields, and `p_btts`. DNB probabilities are
conditioned on no push before calibration metrics are calculated. Settlement
uses the project's 90-minute rules: quarter lines would be split, and a
round-line tie is a push.

## Results

| Population | n | Mean predicted | Hit rate | Gap (hit - predicted) | Brier | Log loss |
|---|---:|---:|---:|---:|---:|---:|
| Selected Pick Teraman | 70 | 82.0% | 80.0% | -2.0pp | 0.1550 | 0.4834 |
| All settleable candidates | 3,546 | 50.0% | 50.0% | 0.0pp | 0.2011 | 0.5870 |
| Pool maximum, one per match | 226 | 81.6% | 81.9% | +0.2pp | 0.1488 | 0.4730 |

The all-candidate reference contains both sides of each market, so its overall
mean is close to 50% by construction. The pool-maximum reference is the more
useful check on probability-ranked selection.

Selected Pick Teraman by market:

| Market | n | Mean predicted | Hit rate | Gap | Brier | Log loss |
|---|---:|---:|---:|---:|---:|---:|
| OU | 56 | 80.9% | 76.8% | -4.2pp | 0.1760 | 0.5366 |
| DC | 14 | 86.4% | 92.9% | +6.4pp | 0.0708 | 0.2706 |

By tier:

| Tier | n | Mean predicted | Hit rate | Gap | Brier | Log loss |
|---|---:|---:|---:|---:|---:|---:|
| Best | 9 | 84.6% | 88.9% | +4.3pp | 0.1033 | 0.3607 |
| Fallback | 61 | 81.7% | 78.7% | -3.0pp | 0.1626 | 0.5015 |

For the all-candidate pool, market gaps are effectively zero: 1X2 n=678,
DC n=678, DNB n=382, OU n=1,356, and BTS n=452. That result reflects the
paired selections in the scan, not a claim that every market is perfectly
calibrated in isolation.

## Answer to the audit question

Using all settleable candidates as the requested pool reference, the selection
effect is selected gap minus pool gap = **-2.0pp (n=70 selected; n=3,546
pool)**. OU contributes the shortfall: **-4.2pp (n=56)**, while DC is **+6.4pp
(n=14)**. The fallback tier carries the negative result (**-3.0pp, n=61**);
the best tier is positive (**+4.3pp, n=9**), a small sample.

Against pure maximum-probability selection, Pick Teraman is also lower by
**-2.3pp**: -2.0pp for selected n=70 versus +0.2pp for pool maximum n=226.
The short window contains **-2.0pp of the headline -5.4pp**, about **38% of
the headline gap's magnitude** (n=70 of the headline n=170). This points to a
selection effect in the window, concentrated in OU, but it does not establish
that the whole model is miscalibrated: the pool-maximum reference is near
calibrated, and the all-candidate aggregate is mechanically balanced.

The archive contained 4,768 market rows for this audit: 3,616 settled or
push, 1,152 excluded because no result was available, and zero unsupported
markets. No corner rows were present in these market-compare snapshots, so
the corner-specific exclusion case did not occur.

## Recommendations

Track OU and fallback selections separately in the next grading window, and
keep the pool-maximum comparison in the recurring audit. Do not recalibrate
the whole model from this 70-row selected subset.

## Coordinator's correction (added at verification, 2026-11-08)

The headline comparison above needs one framing fix. The ledger's
`pick_teraman` leg rows total n=70 across ALL dates — the archive window
contains the product's entire graded history, not 38% of it. The headline
n=170 / -5.4pp figure spans every recommendation product's legs. Recomputed
from the same ledger at verification:

| Product | n | Hit rate | Mean predicted | Gap |
|---|---:|---:|---:|---:|
| pick_teraman | 70 | 80.0% | 82.0% | -2.0pp |
| single | 10 | 50.0% | 56.7% | -6.7pp |
| slip2 legs | 17 | 58.8% | 75.9% | -17.1pp |
| slip5 legs | 16 | 62.5% | 73.4% | -10.9pp |
| slip10 legs | 26 | 61.5% | 66.1% | -4.6pp |
| slip100 legs | 31 | 67.7% | 71.9% | -4.1pp |
| All leg products | 170 | 69.4% | 74.8% | -5.4pp |

So the -5.4pp headline is carried mostly by the slip legs (small samples:
n=16-31 each) and the single (n=10), not by Pick Teraman itself. The
selection-effect reading still holds — the products that select most
aggressively for top probabilities show the largest shortfalls — but the
per-product samples are too small to recalibrate anything yet. All other
numbers in this report were recomputed independently at verification and
match exactly.
