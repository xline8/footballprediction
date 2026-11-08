# Verdict — S-ITB (Italy Serie B SOT) — **FAIL** (dev gate, league-base-rate leg; virgin NOT read)

Prereg: `prereg/PREREG_S_ITB.md` (frozen 369a3a7, before fitting).
Primary line 7.5. Dev n=1,169, virgin 2025/2026 n=390 **not
read**. (X4/X6 not built — era-dead, FEATURES.)

## Dev (LL@7.5 per season and pooled; baselines: league base rate, naive trailing-10)

| Season | Gate Zero | RS | League base rate | Naive |
|---|---|---|---|---|
| 2022/2023 | 0.7098 | 0.7078 | — | — |
| 2023/2024 | 0.6845 | 0.6842 | — | — |
| 2024/2025 | 0.6886 | 0.6877 | — | — |
| **Pooled** | **0.6943** | **0.6933** | **0.6912** | **0.7067** |

## Gate arithmetic

The dev gate requires the pooled LL@7.5 to beat **both**
baselines. Both arms beat the naive trailing-10 comfortably
(GZ 0.6943 < 0.7067) but **lose to the league base rate**
(GZ 0.6943 > 0.6912; RS 0.6933 > 0.6912). The failure is
concentrated in 2022/2023 (GZ 0.7098), the season SOT dropped
to 7.88/match after an 8.33 seed season — the v5 state, built on
the warmer seed, over-prices the line all season, while the
base rate (prior-seasons over-rate, which includes that same
seed) sits closer. At the non-gated lines the picture reverses
(GZ beats both baselines at 6.5: 0.6324 vs 0.6512/0.6427, and
at 8.5: 0.6827 vs 0.7302/0.6948) — recorded for the record;
the gate is at 7.5 and does not move.

RS (ratio-shrink) improves GZ slightly in every season but by
far too little to matter (−0.0010 pooled); its sign check is
moot once the gate fails.

**Verdict: FAIL. Nothing ships.** `engine/sot/results_virgin.json`
records `{"virgin_read": false, ...}` — the virgin window stays
untouched for a future pre-registered attempt.
