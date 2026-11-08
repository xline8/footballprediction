# S-DK verdict — FAIL

Prereg: `prereg/PREREG_S_DK.md` (frozen 6a0240b, before fitting).
Primary line 9.5. Dev pooled n = 579 (2022/2023–2024/2025).

## Dev results — pooled LL@9.5

| Arm / baseline | LL@9.5 |
|---|---|
| Gate Zero (v5 pattern) | 0.6956 |
| RS (ratio-shrink) | 0.6961 |
| X4 (xG/shot) | 0.6965 |
| League base rate | **0.6909** |
| Naive trailing-10 | 0.7078 |

Per season, Gate Zero: 0.6893 / 0.7044 / 0.6931; base rate: 0.6856 /
0.6881 / 0.6990 — the base rate beats Gate Zero in two of three
seasons and on the pool.

## Gate arithmetic

Dev gate: pooled LL@9.5 must beat BOTH baselines. Gate Zero beats
the naive (0.6956 < 0.7078) but **loses to the league base rate
(0.6956 > 0.6909)** — dev gate FAIL. RS and X4 are worse still
(0.6961 / 0.6965), so no variant was positioned to pass either.
Per the prereg, **the virgin window was deliberately NOT read**
(`results_virgin.json` records the reason), and the variants are
moot.

**Verdict: FAIL. Nothing ships.** The unmodified v5 pattern, which
passed cleanly in J1 (S-J1), does not beat a constant prior-seasons
rate in Denmark: DK's SOT level stepped around enough (8.94–9.23 in
dev, 9.70 in the virgin season) that the base-rate baseline is hard
to beat at the 9.5 line, and the model's team structure adds noise
rather than signal at this sample size (12 teams, 579 dev matches).
