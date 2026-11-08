# Verdict — S-FR (FR-Ligue2 shots on target)

**FAIL at virgin leg (i). Nothing ships.**

Calibration: actual − predicted. Primary line 8.5. Prereg:
`prereg/PREREG_S_FR.md`. Dev scored n = 1,065; virgin 2025/2026
n = 306, read ONCE for the two dev-passing arms.

## Dev gate (pooled LL@8.5)

| Arm | LL@8.5 | vs base 0.6948 | vs naive 0.6795 |
|---|---:|---|---|
| Gate Zero | 0.6765 | pass | pass |
| RS | 0.6751 | pass | pass |

RS sign check: RS ≤ GZ in 3/3 dev seasons — eligible.

## Virgin legs (2025/2026)

| Arm | LL@8.5 | Calibration (pp) | SE (pp) |
|---|---:|---:|---:|
| Gate Zero | 0.6703 | −1.23 | 2.79 |
| RS | 0.6691 | −1.32 | 2.79 |
| League base rate | **0.6668** | −2.76 | — |
| Naive trailing-10 | 0.6882 | +0.78 | — |

Leg (i): an arm's virgin LL must be ≤ Gate Zero's **and** ≤ the best
baseline's. The best baseline is the league base rate at 0.6668 —
both arms are worse (GZ +0.0035, RS +0.0023). **Leg (i) FAILS for
both arms.** Leg (ii) alone would have been PROVISIONAL
(|calibration| 1.23 / 1.32pp vs the 1pp boundary, inside 1 SE), but
it is moot under the failed LL leg.

The virgin season ran cold on SOT (over-8.5 rate 38.2% vs 43.7% on
dev), and a constant base-rate probability priced that drop better
than either model's team-level means.

Defect recorded: the SOT harness's `choose()` falls back to Gate
Zero and writes virgin predictions even when no arm is eligible.
It did so here; the coordinator deleted the predictions CSV and
fitted params before commit — nothing ships, per this verdict.
Coordinator verification: dev harness re-run reproduced
`results_dev.json` exactly; virgin numbers are from
`engine/sot/results_virgin.json` (read once).
