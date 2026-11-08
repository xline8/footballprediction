# Verdict — G-RS (RS-SuperLiga goals): **FAIL (dev gate, OU leg)**

Frozen gates: PREREG_G_RS.md (branch `wip-rs-superliga`, commit a0b379d,
before any fitting).

## Dev (season-blocked walk-forward, scored 2022/2023–2024/2025, pooled n = 888 league-member rows)

| Arm | 1X2 LL | RPS | OU2.5 LL |
|---|---|---|---|
| Gate Zero | 0.992930 | 0.207218 | 0.698890 |
| SHRINK | 0.992930 | 0.207218 | 0.698890 |
| X2 | 0.986856 | 0.205114 | 0.696747 |
| Climatology (baseline) | 1.064029 | 0.233579 | **0.695516** |

Per season (Gate Zero model vs climatology, OU2.5 LL):
2022/2023: 0.692730 vs 0.693147 (pass); 2023/2024: 0.715397 vs 0.699363
(fail); 2024/2025: 0.688544 vs 0.694037 (pass).

Gate Zero passes the 1X2 LL and RPS legs but **fails the OU2.5 leg**:
0.698890 > climatology 0.695516 (worse by 0.003374), driven by
2023/2024 (0.715397 vs 0.699363). The pooled failure is narrow, but the
gate is pooled and the leg is binary — there is no near-miss rescue in
the prereg, and the gates are never moved after results are seen.
→ Candidate FAILS at the dev gate. **Virgin 2025/2026 NOT read**
(`results_virgin.json` records `virgin_read: false`). Nothing ships.

Independent verification: the climatology baseline (all three metrics,
pooled and per season) was recomputed from the league CSV with a separate
implementation — exact to all printed digits (1.064029 / 0.233579 /
0.695516). The model's OU failure is therefore in the DC probabilities,
not in the baseline.

## The variant arms (moot, stated plainly)
- SHRINK is numerically identical to Gate Zero in every season (verified
  to full float precision). Under season-blocked fitting this is
  mechanical, as in FI: at each season's fit every team has either 0
  prior in-league matches (entrant; its DC ratings are the unseen
  defaults, and multiplying a rating by n/6 changes nothing that Gate
  Zero does not already do) or ≥30 (a full prior season). No team ever
  sits in the 1–5 match band the arm targets.
- X2 (in-corpus entrant offset, regular-phase entrant rule): the offset
  first fires in 2024/2025 (only 0–2 completed entrant transitions exist
  before 2022/2023–2023/2024, below the frozen minimum of 3; by
  2024/2025 there are 4, GF −0.2855 / GA +0.2078). In 2024/2025 it
  improved all three metrics (1X2 LL 1.002767 vs Gate Zero 1.020988; OU
  LL 0.682115 vs 0.688544) — but pooled it still fails the OU leg
  (0.696747 > 0.695516), and Gate Zero failed dev, so variants are moot
  and no rescue arm may be invented in this prereg.

Diagnosis (recorded, not acted on): a goals-only DC (no xG exists in
this feed in any season) beats climatology on 1X2/RPS here but its
implied totals are worse than a constant over-rate pooled — the failure
concentrates in 2023/2024, the season whose goal level (2.770/match)
sits between the low 2022/2023 (2.430) and the high 2024/2025 (2.882):
the expanding fit's lambdas lag the moving season level. The virgin
season (2.662/match) is inside the dev range, but that observation
cannot change the verdict: the dev gate already failed.
