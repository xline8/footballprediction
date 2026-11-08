# Verdict — G-BO (Bolivia Primera Division goals)

**FAIL — Gate Zero fails the dev gate on the OU2.5 leg. The 2025 virgin
was NOT read. Nothing ships.**

Prereg: `league/BO-PrimeraDivision/prereg/PREREG_G_BO.md` (frozen
ba94d70, before any fitting). Engine: `engine/goals/` (production
Dixon-Coles port, goals-only — no xG or shotmap exists in this league).

## Dev gate (season-blocked walk-forward; seed 2021 regular n=240, scored 2022–2024 regular n=896)

| arm | 1X2 LL | RPS | OU2.5 LL |
|---|---|---|---|
| Gate Zero | 0.993593 | 0.205238 | **0.698485** |
| SHRINK | 0.993593 | 0.205238 | **0.698485** |
| climatology | 1.022474 | 0.213618 | 0.693243 |

- 1X2 LL and RPS beat climatology ✓. OU2.5 LL loses to climatology by
  0.0052 ✗ → **dev gate FAIL**. Per-season OU2.5 LL (model vs
  climatology): 2022 0.7137 vs 0.6955 ✗; 2023 0.6655 vs 0.7013 ✓;
  2024 0.7120 vs 0.6836 ✗ — the failure is broad, not one season.
- SHRINK is identical to Gate Zero in every season: the arm is vacuous
  in this design (at each block start every team has 0 or 30+ prior
  in-league matches, so n/6 is 0 or 1 and no rating is ever shrunk).
  Recorded, not re-designed — the prereg froze the arm.
- Climatology OU2.5 LL independently recomputed from the per-match CSV
  = 0.693243 (exact match).

## Virgin — 2025 regular (n=240, complete)

**Not read.** Gate Zero failed dev, so under the frozen rule the virgin
is not read and no arm is evaluated on it. The 2025 season is a genuine
goals outlier (mean 3.62 vs 2.76–3.06 in the other seasons; event Goal
counts confirm the score totals), which would have made the virgin hard
— but the window was not moved and the verdict does not depend on it.
Confirmatory 2026 (in progress, rounds 1–25) is reserved.

## Frozen halves constant

Goals 1H share **0.4323** (2021–2024 regular, ratio-of-sums; true
variance ≤ 0 by split-half decomposition).
