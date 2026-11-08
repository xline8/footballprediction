# Verdict — G-BG (goals): FAIL at the dev gate. Virgin NOT read.

Prereg: `prereg/PREREG_G_BG.md` (frozen before fitting). Dixon-Coles,
goals-only (no xG exists in this league), season-blocked walk-forward,
seed 2021/2022, dev 2022/2023–2024/2025 (n = 859).

## Dev results (pooled, vs climatology)

| Arm | 1X2 LL | RPS | OU2.5 LL |
|---|---|---|---|
| Gate Zero | **1.0042** | **0.2099** | 0.7002 |
| SHRINK | 1.0042 | 0.2099 | 0.7002 |
| Climatology | 1.0681 | 0.2337 | **0.6853** |

Per season (model 1X2 LL vs climatology): 2022/2023 1.0074 vs 1.0684;
2023/2024 0.9829 vs 1.0626; 2024/2025 1.0217 vs 1.0732 — the model
beats climatology on 1X2 in every dev season, and on RPS pooled
(0.2099 < 0.2337). SHRINK is row-identical to Gate Zero, exactly the
possibility the prereg recorded in advance (under season-blocked
fitting a team's prior count is 0 or ≥ a full season, so the <6-match
shrinkage never binds).

## Gate arithmetic

Dev gate requires pooled 1X2 LL AND RPS to beat climatology AND
OU2.5 LL to beat the base-rate baseline. Legs 1–2 pass; the OU2.5
leg fails: 0.7002 > 0.6853 (the model's totals are worse than the
climatology over-rate in all three dev seasons: 0.6999/0.7014/0.6994
vs 0.6775/0.6922/0.6862). **Gate Zero fails its dev gate ⇒ variants
are moot, the verdict is FAIL, and the virgin (2025/2026) was NOT
read.** Nothing ships. All dev numbers were recomputed independently
from `engine/goals/predictions_dev.csv` — exact agreement.
