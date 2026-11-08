# Verdict — S-MA (Morocco Botola Pro SOT)

**FAIL at the dev gate. Virgin NOT read. Nothing ships.**

Prereg: `prereg/PREREG_S_MA.md`. Dev = rich-era scored window
2025-01-01 – 2025-05-12, n=109, per-match walk-forward after the
Nov–Dec 2024 warm-up. All numbers recomputed by the coordinator
from `engine/sot/predictions_dev.csv` (arm and baseline
probabilities are both in the CSV); they match
`results_dev.json` exactly.

## Dev LL @ 7.5 (pooled, n=109)

| arm / baseline | LL@7.5 | mean P(over 7.5) |
|---|---|---|
| Gate Zero (v5) | 0.6939 | 0.4352 |
| RS (BB prior 20,000) | 0.6942 | 0.4351 |
| league base rate | **0.6935** | 0.5011 |
| naive trailing-10 | 0.7087 | 0.4247 |

Actual over-rate 0.4128; actual mean total 6.94 vs model mean
7.32.

Dev gate (verbatim): pooled dev LL@7.5 must beat BOTH baselines.
Gate Zero beats naive (0.6939 < 0.7087) but loses to the league
base rate by 0.0004 (0.6939 > 0.6935). That is a failure of the
gate as frozen — the margin is tiny and is reported as tiny, but
gates are not moved after results. Gate Zero failing its dev gate
makes RS moot; the virgin (2025/2026) is NOT read; S-MA is FAIL.

Context, not excuse: the v5 pattern's team structure adds nothing
over the league rate on this short rich-era dev window (109
matches, SOT trait r ≈ 0.40/0.45 in EDA). A future prereg with a
second rich dev season may retest; this prereg is closed.

No fitted params ship, no predictions. Production code untouched.
