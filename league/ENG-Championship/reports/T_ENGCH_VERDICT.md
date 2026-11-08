# Verdict — T-ENGCH (England Championship total shots) — **FAIL** (virgin legs (i) + (ii))

Prereg: `prereg/PREREG_T_ENGCH.md`. Primary line 23.5. Dev n=1,671,
virgin 2025/2026 n=555.

## Dev (pooled LL@23.5; baselines: league 0.6936, naive 0.6896)

| Arm | Dev LL | Sign vs A | Dev gate |
|---|---|---|---|
| A (v1) | 0.6805 | — | PASS |
| B (v2 level layer) | 0.6805 | 1/3 | PASS (sign leg applies at both-pass) |
| C (E9 trailing-r) | 0.6809 | 0/3 | PASS (sign leg applies at both-pass) |

All three arms passed the dev gate and were read on the virgin,
per the total-shots family's mechanical reading (as T-SCO).

## Virgin 2025/2026

| Arm | LL@23.5 | Calibration (SE) | Legs |
|---|---|---|---|
| A | 0.6635 | −3.92pp (2.05pp) | (i) FAIL vs naive; (ii) FAIL |
| B | 0.6626 | −3.21pp (2.05pp) | (i) FAIL vs naive; (ii) FAIL; sign 1/3 FAIL |
| C | 0.6639 | −3.85pp (2.06pp) | (i) FAIL vs naive; (ii) FAIL; sign 0/3 FAIL |
| Baselines | league 0.6776 / **naive 0.6622** | naive −0.21pp | |

Gate arithmetic: leg (i) requires LL ≤ the reference arm's AND ≤
the best baseline's — the naive trailing-10 (0.6622) beats every
arm, so all three fail leg (i). Leg (ii) also fails for all three:
calibration breaches of 3.2–3.9pp exceed the 1pp boundary by more
than 1 SE (2.05pp). **FAIL; nothing ships** (`shipped_arm: null` in
`results_virgin.json`; no predictions CSV).

What happened, plainly: the virgin season ran **hot** on shots —
25.22/match vs the dev window's 23.99, over-23.5 rate 60.5% vs
51.5% (recomputed from the raw CSV) — and the ratings-based arms,
anchored to slower history, under-predicted it, while the naive
trailing-10 (a pure recent-form tracker) adapted within the season.
The same failure shape as T-AR. The dev gate cannot see a level
shift that only arrives in the virgin season; that is what the
virgin is for.
