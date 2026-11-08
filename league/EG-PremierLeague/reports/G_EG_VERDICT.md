# Verdict — G-EG (Egypt Premier League goals model) — **FAIL** (dev gate, OU2.5 leg; virgin NOT read)

Prereg: `prereg/PREREG_G_EG.md` (frozen 6b86220, before fitting).
Dev = season-blocked walk-forward, seed 2021/2022, scored
2022/2023 + 2023/2024 + 2024/2025 (pooled n = 837). X1 is goals-only
in every fold (xG exists only from the virgin season).

## Dev (pooled)

| Arm | 1X2 LL | RPS | OU2.5 LL | vs climatology / base rate |
|---|---|---|---|---|
| Gate Zero | 1.0106 | 0.1971 | 0.6968 | LL ✓ (1.0966), RPS ✓ (0.2238), **OU2.5 ✗ (0.6761)** |
| SHRINK | 1.0106 | 0.1971 | 0.6968 | identical to Gate Zero (see below) |
| Climatology | 1.0966 | 0.2238 | 0.6761 | — |

Per-season OU2.5 LL (model vs base rate): 2022/2023 0.7339 vs
0.6773 ✗; 2023/2024 0.6939 vs 0.6875 ✗; 2024/2025 0.6505 vs
0.6591 ✓. The DC model beats climatology clearly on 1X2/RPS in
every season but its total-goals distribution is worse than the
base rate in two of three dev seasons — the pooled OU2.5 leg
fails, so the dev gate fails.

SHRINK is mathematically inert in this league's season-blocked
folds, verified directly: at every fold cutoff (and at the virgin
cutoff) each club has either 0 prior in-league matches (promoted
from outside the warehouse; n = 0 ⇒ SHRINK ≡ Gate Zero by its own
rule) or ≥ 34 (≥ the 6-match threshold). No club ever sits in the
1–5 match band the arm exists for, so the arm's numbers equal
Gate Zero's exactly. That is a property of the design in this
league, not an implementation bug.

## Virgin

**NOT read.** Gate Zero failed its own dev gate ⇒ variants moot,
verdict FAIL, per the frozen mechanical reading. 2025/2026 and
2026/2027 rows were never loaded by the goals harness beyond the
dev season set.

**Ships: nothing.** G-EG is a complete FAIL.
