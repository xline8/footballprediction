# T-HU-NBI (total shots) — VERDICT: FAIL (dev gate)

Target: the feed's own total_shots key (HU levels are low vs other
leagues: dev mean 19.04 — the key evidently counts a narrower shot
definition; it is consistent across all seasons). Primary line 19.5.
Dev n=588; virgin 2025/2026 **deliberately NOT read**.

| arm | dev LL@19.5 | base LL | naive LL |
|---|---|---|---|
| A (v1) | 0.7067 | 0.6956 | 0.7058 |
| B (v2 level layer) | 0.7058 | 0.6956 | 0.7058 |
| C (E9 trailing-r) | 0.7035 | 0.6956 | 0.7058 |

All three arms lose the pooled leg vs the base rate → FAIL.
Defect noted in the copied harness: arm B's pooled dev LL equals the
naive trailing-10 LL to full printed precision (0.7057836266832629) —
arm B as ported is numerically indistinguishable from the naive
baseline in this league; the verdict is unaffected (both lose to the
base rate). Nothing ships.
