# Phase 1 — EDA: Egypt Premier League

All figures below are copied from eda_numbers.json; no modelling or virgin-season modelling is performed.

## F1. Levels

| Season | Goals | xG | SOT | Corners | Shots | Yellows stats | Yellows events | Reds |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2021/2022 | 2.199 | — | 7.282 | 9.439 | 22.393 | 2.118 | 0.085 | 0.141 |
| 2022/2023 | 2.147 | — | 7.194 | 9.502 | 22.445 | 3.278 | 0.101 | 0.207 |
| 2023/2024 | 2.386 | — | 7.558 | 9.231 | 22.597 | 3.878 | 0.111 | 0.205 |
| 2024/2025 | 2.142 | 1.600 | 6.866 | 8.973 | 21.612 | 3.869 | 3.884 | 0.189 |
| 2025/2026 | 2.022 | 2.014 | 6.894 | 9.093 | 21.593 | 3.957 | 4.180 | 0.283 |
| 2026/2027 | 2.312 | 2.228 | 7.638 | 9.162 | 24.663 | 3.337 | 3.650 | 0.200 |

The 2025/2026 row is inventory only; 2026/2027 is reserved.

## F2. Reliability

| Trait | Career r | 2023/2024–2024/2025 r |
|---|---:|---:|
| Goals for / against | 0.851 / 0.816 | 0.753 / 0.553 |
| SOT for / against | 0.821 / 0.628 | 0.774 / 0.391 |
| Corners for / against | 0.803 / 0.681 | 0.646 / 0.213 |
| Stats yellows for / against | 0.766 / 0.856 | 0.262 / 0.521 |
| Total shots for / against | 0.810 / 0.733 | 0.856 / 0.673 |
| Touches for / against | 0.877 / 0.695 | 0.791 / 0.719 |
| Possession | 0.921 | 0.903 |
| Big chance | 0.730 | 0.785 |

## F3. Half constants and variance decomposition

Complete-split dev seasons are 2023/2024 and 2024/2025 only. Shares are goals **0.4202**, SOT **0.4445**, corners **0.4604**, shots **0.4459**, and stats yellows **0.3609**. True SD after subtracting estimated binomial noise is respectively **0.0000, 0.0157, 0.0162, 0.0000, 0.0563**. The goals time-coverage input is **100.0%** in both seasons.

## F4. Home edge

Home-edge (home goals minus away goals), by season, is **+0.127, +0.160, +0.163, +0.071, +0.065, −0.087** (2021/2022 → 2026/2027); pooled dev (≤2024/2025) is **+0.135**. Home-win rates are **36.9%, 38.6%, 37.9%, 34.2%, 33.9%, 37.5%**, with pooled dev **37.1%**. (Coordinator correction 2026-11-09: an earlier draft of this paragraph carried numbers that contradicted eda_numbers.json; the JSON values above are the verified ones, recomputed independently from eg_matches.csv.)

## F5. Primary dev lines

| Era | SOT | Corners | Shots | Stats yellows | Goals OU2.5 |
|---|---|---|---|---|---:|
| 2022/2023–2024/2025 | 6.5 (55.1%) | 8.5 (55.6%) | 22.5 (47.3%) | 3.5 (52.8%) | 40.4% |
| 2023/2024–2024/2025 | 7.5 (44.6%) | 8.5 (54.3%) | 21.5 (53.1%) | 3.5 (56.0%) | 40.3% |

Ladder over-rates are preserved in the JSON for every line.

## F6. Referee and cards

Dev referee split-half reliability for stats yellows is **r=0.290** across **32** referees meeting the 10-match threshold. Referee coverage is **62.1%, 81.4%, 71.9%, 75.6%, 26.7%, 100.0%** by season. Full cards agreement and stats-missing counts are in the JSON audit. Stats-feed yellows level rises steeply across the dev era (2.118 → 3.278 → 3.878 → 3.869 per match); 2021/2022 is warm-up/seed only and never scored, and the count harnesses' prior-season base rates absorb part of the trend. The 2024/2025 xG figure in F1 (1.600) is the mean over the single match with xG that season (0.4% coverage), not a season level.

## F7. Brief discrepancies

The measured values differ from the brief’s approximate sampled expectations in several places: shotmap/xG are **0.0% through 2023/2024**, **0.4% in 2024/2025**, and start at **100.0% in 2025/2026**; touches are **39.2%, 68.6%, 93.8%, 98.7%, 100.0%, 100.0%**; referee coverage is **62.1%, 81.4%, 71.9%, 75.6%, 26.7%, 100.0%**. These exact built-CSV measurements are used.
