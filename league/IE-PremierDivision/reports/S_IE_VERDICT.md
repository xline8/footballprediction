# Verdict — S-IE (Ireland Premier Division SOT) — **FAIL** (dev gate; virgin NOT read)

Prereg: `prereg/PREREG_S_IE.md`. Primary line 7.5. Arms: Gate Zero
(v5 pattern) + RS (BB prior 200 → 20,000). X4/X6 were never built:
the shotmap era is 2025+ (ERA-INSUFFICIENT).

## Dev (walk-forward, warm-up 2022, scored 2023–2025, n = 540)

| | LL@7.5 |
|---|---|
| League base rate | **0.6908** |
| Gate Zero | 0.6941 |
| RS | 0.6942 |
| Naive trailing-10 | 0.7118 |

The base-rate baseline was recomputed independently from the CSV
(prior-seasons over-7.5 rate per target season: 0.6865 / 0.7016 /
0.6843, pooled 0.6908 — exact match).

Gate Zero beats the naive baseline but **loses to the plain league
base rate by 0.0033 LL**, and RS is a hair worse than Gate Zero —
the dev gate requires beating BOTH baselines, so both arms are
dead at dev. Per the frozen rule the virgin window (2026) was
**deliberately NOT read** and stays unburned. Nothing ships; no
predictions CSV.

Context: IE total SOT is low and stable (7.81–8.48/match across
2022–2025) and the over-7.5 rate sits near the line, so a constant
prior-seasons rate is a hard baseline at this line; the v5 team's
ratings add variance without adding discrimination here.
