# Phase A2 — Exploratory Data Analysis

All values below come from `eda_summary.json`. The decisive finding is a
regime break: 2024 is materially higher than 2021–2023 in goals (2.78→3.13),
SOT (8.50→9.81), total shots (24.6→27.8), and corners (9.40→10.49). Cards
step earlier, from 2.75–2.85 in 2021–2022 to 3.72+ from 2023.

## Levels and home advantage

| Season | Goals | SOT | Total shots | Corners | Stats yellows | Goal home edge |
|---|---:|---:|---:|---:|---:|---:|
| 2021 | 2.5398 | 8.0170 | 22.7670 | 9.0795 | 2.8523 | 0.2330 |
| 2022 | 2.8595 | 8.1946 | 22.9329 | 8.8087 | 2.7450 | 0.2124 |
| 2023 | 2.7750 | 8.5042 | 24.6458 | 9.4042 | 3.7208 | 0.3250 |
| 2024 | 3.1250 | 9.8083 | 27.8292 | 10.4917 | 3.7625 | 0.4667 |
| 2025 | 3.2125 | 9.3292 | 26.6708 | 10.0375 | 3.9000 | 0.3875 |
| 2026 | 3.1750 | 9.0333 | 26.4083 | 9.9875 | 3.7917 | 0.4583 |

2021 is a COVID-era group/playoff competition; 2022 has 18 teams and eight
stats-missing rows. These are additional reasons to exclude both from fitting.
The 2023 card step and 2024 level step are not model noise to be averaged
away. All production fits therefore use 2023+ only.

## Reliability and halves

In the dev block (2023–2025), split-half reliability is SOT for/against
0.778/0.689, corners-for 0.624, total shots for/against 0.742/0.726, goals
for 0.838, and yellow cards for/against 0.282/0.347. Opp-box touches are
0.745/0.620. The weak yellows result is recorded honestly; it does not change
the frozen cards target.

First-half shares have variance ratios 0.95–1.12 for the five model markets,
consistent with binomial sampling noise. Frozen shares are goals 0.4458, SOT
0.4580, corners 0.4711, total shots 0.4594, and yellow cards 0.3328.
Every market has a legitimate split source; none is FT-only.

## Referee and territorial findings

Referee strictness reliability is 0.218 in the dev block, with block values
0.133, 0.014, and −0.703 across the wider splits. Combined with the coverage
collapse to 64.58% in 2025 and 48.75% in 2026, referee strictness is dropped.
Touches coverage is 55% in 2023 and complete from 2024; it remains a gated
corners arm with the eight-match fallback rule.

## Primary lines

The scored-dev distribution selects SOT 9.5 (over 0.494), corners 9.5
(0.562; 10.5 is 0.431), cards 3.5 (0.537), and total shots 26.5 (0.537;
27.5 is 0.454). Report ladders are SOT 8.5/9.5/10.5, corners 8.5/9.5/10.5,
cards 3.5/4.5, and total shots 25.5/26.5/27.5.
