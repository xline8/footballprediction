# Verdict — S-AT2 (Austria 2. Liga shots on target)

**FAIL — at the dev gate. Virgin window NOT read.**

## Dev (walk-forward; scored 2022/2023–2024/2025, stats n = 708, LL @ 8.5)

| arm | LL @ 8.5 | per-season LL |
|---|---|---|
| Gate Zero | 0.704212 | 0.683423 / 0.674704 / 0.753034 |
| RS (ratio prior 200 → 20,000) | 0.702097 | — |
| league base rate | 0.694736 | |
| naive trailing-10 | 0.780604 | |

Gate Zero beats the naive baseline decisively but **loses to the
league base rate** (0.704212 > 0.694736) → **dev gate FAIL**. RS
improves Gate Zero slightly (0.702097) and still loses to the base
rate; with Gate Zero dead the variant is moot under the frozen
rule. Verdict FAIL; season 2025/2026 was **not read** by this
candidate. Nothing ships.

Reading: the failure is concentrated in 2024/2025 (LL 0.753034 vs
0.683/0.675 in the clean dev seasons) — the season whose shot/SOT
counting definition breaks in the feed (EDA F12, frozen in the
prereg before fitting). In the two clean dev seasons the v5
pattern is competitive; priced against a base rate pooled over a
window containing the contaminated season, it cannot clear the
gate. That is the gate doing its job on a corrupted series: the
candidate is failed as registered, not rescued by window surgery.

Coordinator notes: pooled LLs recomputed independently from
`engine/sot/predictions_dev.csv` (708 rows per arm); match the
harness to 6dp.
