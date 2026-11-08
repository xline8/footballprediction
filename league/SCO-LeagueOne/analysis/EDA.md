# Phase A — Exploratory Data Analysis: SCO League One

All numbers below are from `eda_summary.json` (coverage facts are also in `inventory_summary.json`). This is descriptive only; no season is fitted.

## Levels and lines

| season | goals/match | home goal share | Yellow/match | Yellow+YellowRed/match | Red events/match | HT goal share | HT Yellow share | OU2.5 | Yellow O3.5 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2021/2022 | 2.816667 | 0.526627 | 3.616667 | 3.733333 | 0.266667 | 0.388560 | 0.336406 | 0.533333 | 0.516667 |
| 2022/2023 | 2.961111 | 0.547842 | 3.533333 | 3.611111 | 0.183333 | 0.409006 | 0.297170 | 0.561111 | 0.461111 |
| 2023/2024 | 3.172222 | 0.516637 | 3.644444 | 3.694444 | 0.161111 | 0.469352 | 0.303354 | 0.622222 | 0.483333 |
| 2024/2025 | 2.700000 | 0.504115 | 3.527778 | 3.627778 | 0.211111 | 0.438272 | 0.318110 | 0.516667 | 0.461111 |
| 2025/2026 | 2.644444 | 0.535714 | 4.127778 | 4.155556 | 0.105556 | 0.439076 | 0.314939 | 0.494444 | 0.605556 |
| 2026/2027 partial | 2.884058 | 0.562814 | 4.623188 | 4.623188 | 0.057971 | 0.417085 | 0.313480 | 0.608696 | 0.753623 |

The K target is Yellow only. On the development seasons 2022/2023–2024/2025, OU2.5 is 0.566667 (n=540) and Yellow O3.5 is 0.468519 (n=540). These are the primary lines. SOT, corners, and total-shots levels are absent, not zero.

## Reliability

Using within-season first-half versus second-half team rates, pooled over complete seasons 2021/2022–2025/2026 (50 team-season observations): goals for r=0.410642 and against r=0.578946; event Yellow for r=0.387955 and against r=0.534905.

## Halves constants

On complete seasons, pooled first-half goal share is 0.429460 with observed variance 0.10373353, binomial-noise variance 0.10787212, and true variance −0.00413859: NOISE, so frozen as a constant. Event Yellow share is 0.314062 with observed variance 0.07496799, expected noise 0.07494742, and true variance 0.00002057 — an implied per-match SD of ≈0.5pp, negligible, so frozen as a constant too. The partial 2026/2027 season is not used for these constants.

Mover evidence is frozen in `movers.json`. Down-from-Championship entrants have pooled ΔGF +0.176190 and ΔGA −0.288095; `up_other` entrants have pooled ΔGF −0.136111 and ΔGA +0.200694. `up_other` means “promoted from below, tier unverified”; the League Two label is not inferred. The per-season signs are recorded there.
