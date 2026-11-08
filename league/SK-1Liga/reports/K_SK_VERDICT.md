# Verdict — K-SK (SK-1Liga cards, event-unified yellows, Gate Zero only)

**FAIL — dev gate. Virgin NOT read. Nothing ships.**

Dev (pooled, n = 576, LL@3.5):

| | LL@3.5 | Dev gate |
|---|---|---|
| Gate Zero | 0.690307 | FAIL |
| League base rate | **0.681903** | |
| Naive trailing-10 | **0.690175** | |

Per-season Gate Zero LL@3.5 vs base / naive: 2022/2023 0.677512
vs 0.683122 / 0.678201 ✓✓; 2023/2024 0.707926 vs 0.689591 /
0.713098 ✗ (base); 2024/2025 0.685484 vs 0.672997 / 0.679227 ✗✗.
The model wins the first dev season and loses the next two; the
pooled result loses to the league base rate by +0.0084 and even
to the naive trailing-10 by +0.0001. This is consistent with the
EDA: SK's yellows-for team trait is the weakest measured in this
league (split-half r = 0.194), so team ratings add noise rather
than signal at the 3.5 line, while the base rate — a constant —
is hard to beat when the level oscillates season to season
(3.66 → 4.18 → 3.82 → 4.36 in the seed/dev seasons).

Gate arithmetic (PREREG_K_SK): the dev gate requires pooled dev
LL@3.5 to beat BOTH baselines. It beats neither → the candidate
is dead and the virgin is NOT read. The refusal was exercised
through the harness itself: `run_k_sk.py virgin --arms gate_zero`
exits with "virgin refused non-passing arm(s): gate_zero" before
loading any virgin row; no `results_virgin.json` exists.

Ships: nothing. No predictions, no fitted params.
