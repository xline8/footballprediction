# Verdict — T-CA (CA-PremierLeague total shots model)

**FAIL — all three arms fail the dev gate against naive
trailing-10; virgin NOT read.**

Dev (pooled, n = 336, LL@22.5):

| Arm | LL@22.5 | vs base 0.696515 | vs naive 0.686318 | Dev gate |
|---|---|---|---|---|
| A (v1 pattern) | 0.687676 | ✓ | ✗ | FAIL |
| B (v2 level layer) | 0.687951 | ✓ | ✗ | FAIL |
| C (E9 trailing-r) | 0.687220 | ✓ | ✗ | FAIL |

Gate arithmetic (PREREG_T_CA): the dev gate requires pooled
LL@22.5 to beat BOTH baselines. Every arm beats the league base
rate and every arm loses to naive trailing-10 — Arm C, the best,
by 0.0009 (0.687220 vs 0.686318). All arms are dead; per the
prereg, if Arm A fails its dev gate the variants are moot and
the virgin is NOT read. (Arm C's per-season sign check vs A
would also have failed: 2022 ✓, 2023 ✗, 2024 ✗ → 1 of 3.)

Total-shots team traits are present but weak in this league
(split-half r ≈ 0.24–0.63 by season pair, EDA), and with 8 clubs
the trailing-10 mean of the target itself captures nearly all of
the usable signal at the 22.5 line.

Ships: nothing. Virgin read: NO (deliberately unread).
