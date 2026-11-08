# Verdict — G-MA (Morocco Botola Pro goals)

**FAIL at the dev gate. Virgin NOT read. Nothing ships.**

Prereg: `prereg/PREREG_G_MA.md`. Dev n=720 (2022/2023–2024/2025,
season-blocked walk-forward). All numbers recomputed by the
coordinator from `engine/goals/predictions_dev.csv` and the league
CSV; they match the engine's `results_dev.json` exactly.

## Dev (pooled)

| arm | 1X2 LL | RPS | OU2.5 LL |
|---|---|---|---|
| Gate Zero | 1.0086 | 0.1988 | 0.6894 |
| SHRINK | 1.0086 | 0.1988 | 0.6894 |
| climatology / base | 1.0843 | 0.2225 | 0.6768 |

Per-season 1X2 LL (Gate Zero vs climatology): 1.0245 vs 1.0857,
1.0109 vs 1.0867, 0.9905 vs 1.0806 — the DC pattern beats
climatology on 1X2 and RPS in every dev season and pooled. But the
dev gate (verbatim) requires OU2.5 LL to also beat the base-rate
baseline: 0.6894 > 0.6768 — Gate Zero FAILS the OU leg. Per the
frozen mechanical reading, Gate Zero failing its own dev gate
closes the candidate: SHRINK is moot, the virgin (2025/2026) is
NOT read, G-MA is FAIL.

SHRINK finding: numerically identical to Gate Zero on all 720 dev
rows — under season-blocked expanding fits every team at
prediction time has either 0 prior in-league matches (entrant;
ratings = league mean in both arms) or ≥30, so the 1–5 match band
never occurs (same finding as G-SCOCH / G-RU1).

The pattern is the program's familiar one: in a very low-scoring
league (2.13–2.31 goals/match) the DC's totals are too dispersed
for the OU2.5 line even while its 1X2 ranking is clearly better
than climatology. The gate is the gate; no rescue arm exists in
this prereg.

No fitted params ship, no predictions. Production code untouched.
