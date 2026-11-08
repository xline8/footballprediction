# Verdict — K-BG (cards): FAIL at the dev gate. Virgin NOT read.

Prereg: `prereg/PREREG_K_BG.md`. Production cards pattern, target
total event-unified yellows (the stats feed publishes no yellow key
in this league — Step 1), primary line 4.5, warm-up 2021/2022, dev
scored 2022/2023–2024/2025 (n = 859).

## Dev results (pooled LL@4.5)

| Arm | Dev LL@4.5 | vs league base 0.6804 | vs naive 0.6862 |
|---|---|---|---|
| Gate Zero | 0.6855 | **fail** | pass |
| X8 (referee) | 0.6767 | pass | pass |

Per season (model LL@4.5): Gate Zero 0.6675 / 0.6872 / 0.7012 —
deteriorating across the dev window; X8 0.6563 / 0.6883 / 0.6853.

## Gate arithmetic

The dev gate requires the pooled LL@4.5 to beat BOTH baselines.
Gate Zero beats the naive (0.6855 < 0.6862) but **loses to the
league base rate (0.6855 > 0.6804)** ⇒ Gate Zero fails its dev gate.
Per the prereg's frozen mechanical rule — Gate Zero dev failure ⇒
variants are moot — X8's passing dev comparison (0.6767, the referee
multiplier genuinely helped: strictness r = 0.379 at ~100% coverage)
does **not** rescue the candidate, no rescue arm may be invented,
and **the virgin (2025/2026) was NOT read**. The engine's virgin
entry point fails closed on exactly this condition. Nothing ships.

This is the honest cost of the frozen rule, recorded plainly: the
one arm that beat both baselines in dev is unusable because the
reference arm it modifies failed first. Team yellow traits were the
weakest reliability in this league's EDA (0.229/0.334), and the base
model's deterioration across dev seasons is consistent with that.
All numbers recomputed independently from
`engine/cards/predictions_dev.csv` — exact agreement.
