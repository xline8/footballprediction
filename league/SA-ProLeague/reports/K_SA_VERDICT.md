# Verdict — K-SA (Saudi Pro League cards) — **FAIL** (dev gate; virgin NOT read)

Prereg: `prereg/PREREG_K_SA.md` (frozen aa3a34d, before fitting).
Dev = walk-forward scored on post-break seasons 2023/2024 +
2024/2025 (n=612), warm-up 2021/2022–2022/2023; virgin = 2025/2026
(n=306) was **deliberately NOT read** — Gate Zero, the only arm,
failed the dev gate. Target: unified event-feed yellows
(DATA_UNDERSTANDING §3.1).

## Dev (LL@3.5)

| Season | Model (Gate Zero) | League base rate | Naive trailing-10 |
|---|---|---|---|
| 2023/2024 | 0.6828 | 0.6818 | 0.6791 |
| 2024/2025 | 0.6688 | 0.6681 | 0.6763 |
| **Pooled** | **0.6758** | **0.6750** | **0.6777** |

Gate arithmetic: the frozen dev gate requires the pooled model LL
to beat BOTH baselines. 0.6758 > 0.6750 — the model loses to the
league base rate pooled, and loses at least one baseline in each
dev season (naive in 2023/2024, base rate in 2024/2025).
`dev_gate_pass = false` in `engine/cards/results_dev.json`.

**Ships: nothing.** The EDA said this was the likely outcome and
the gate confirmed it mechanically: team yellow traits in this
league are weak (split-half r = 0.264 post-era, vs 0.639 in SCO),
referee strictness is noise (r = −0.279) *and* unnamed in 99.3% of
virgin-season matches, so there was nothing reliable for the
reference architecture to extract beyond the league level — and
the league level is the baseline it had to beat. No rescue arm
was invented; the 2026/2027 confirmatory window stays reserved.
