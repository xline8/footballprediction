# Verdict — K-ES (ES-LaLiga2 cards) — **FAIL** (dev gate; virgin deliberately NOT read)

Prereg: `prereg/PREREG_K_ES.md`. Primary line 4.5, target =
event-feed yellows (Phase 1 §3). Gate Zero only (X8 dropped in
FEATURES, referee r = 0.180). Dev n=1,404, virgin 2025/2026 n=468
**not read**.

## Dev (LL@4.5)

| Season | Gate Zero | League base rate | Naive trailing-10 |
|---|---|---|---|
| 2022/2023 | 0.6909 | 0.6880 | 0.6784 |
| 2023/2024 | 0.7001 | 0.6939 | 0.6998 |
| 2024/2025 | 0.6863 | 0.6933 | 0.6811 |
| **Pooled** | **0.6924** | **0.6917** | **0.6864** |

Gate arithmetic: the dev gate requires the pooled LL@4.5 to beat
BOTH baselines. Gate Zero beats neither — it trails the league base
rate by 0.0007 and the naive trailing-10 by 0.0060 (it wins a single
season against each: base rate in 2024/2025, naive in 2023/2024).
The arm is dead at the dev gate. **Virgin NOT read; nothing ships.**

Read against the base rates: unlike ENGCH (where the yellows trait
itself was noise, r = −0.01), the ES team yellows trait is real
(EDA F2, r = 0.453) — the failure here is the reference
architecture's, not the trait's: the ratings + ensemble machinery
adds nothing over a trailing-10 mean of the same counts in this
league, and the pooled margin is not close against the naive
baseline. That is a complete, respectable FAIL; no rescue arm is
invented, per the frozen rules.

**Ships: nothing.** K-ES is FAIL.
