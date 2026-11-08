# Verdict — G-SA (Saudi Pro League goals) — **FAIL** (dev gate; virgin NOT read)

Prereg: `prereg/PREREG_G_SA.md` (frozen aa3a34d, before fitting).
Dev = walk-forward scored on post-break seasons 2023/2024 +
2024/2025 (n=612), seed 2021/2022–2022/2023; virgin = 2025/2026
(n=306) was **deliberately NOT read** — no arm passed the dev gate.

## Dev (pooled, n=612)

| Arm | 1X2 LL | RPS | OU2.5 LL | vs climatology (1.0673 / 0.2384 / 0.6881) |
|---|---|---|---|---|
| Gate Zero | 0.9842 | 0.2069 | 0.6951 | beats LL ✓ and RPS ✓, **OU leg ✗** |
| SHRINK | 0.9842 | 0.2069 | 0.6951 | identical to GZ — **OU leg ✗** |
| X3 | 0.9949 | 0.2096 | 0.7085 | beats LL/RPS, **OU leg ✗** (worse) |

Per-season OU2.5 LL (model vs climatology): 2023/2024 0.7027 vs
0.6900; 2024/2025 0.6875 vs 0.6862 — the model loses the OU leg in
both dev seasons, not just pooled.

Gate arithmetic: the frozen dev gate requires pooled 1X2 LL **and**
RPS **and** OU2.5 LL all to beat climatology. Every arm fails the
OU2.5 leg (Gate Zero by +0.0070). Gate Zero failing its own dev
gate makes the variants moot per the prereg's mechanical reading.

**Ships: nothing.** This is the regime break collecting its price
in the open: the DC's 1X2 discrimination survives the break
comfortably (LL 0.984 vs 1.067), but its totals calibration does
not — fits anchored in pre-break / early post-break data misprice
the post-break scoring level (2.68 → 2.96 goals/match) by enough
that a constant base rate beats the model's OU probabilities in
both post-break dev seasons. No rescue arm was invented; the
2026/2027 confirmatory window stays reserved.
