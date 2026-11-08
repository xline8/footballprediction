# Phase 4 — Model Design: IE-PremierDivision candidates

No fitting is performed in Phase A. The design frame is seed 2021, dev
evaluation 2022–2025, and virgin 2026. All line rates and selected lines are
frozen in `eda_numbers.json`.

| Candidate | Reference / dev window | Frozen arms |
|---|---|---|
| G-IE | DC goals-only; goals OU 1.5/2.5/3.5, 2022–2025 | Gate Zero + SHRINK |
| S-IE | SOT v5; 7.5/8.5/9.5, 2023–2025 (n=540) | Gate Zero + RS, BB prior 200→20000 |
| C-IE | corners v3; 9.5/10.5/11.5, 2023–2025 (n=540) | Gate Zero with X9 + X7 |
| K-IE | event-unified cards; 3.5/4.5/5.5, 2022–2025 (n=720) | Gate Zero; no X8 |
| T-IE | total shots; 23.5/24.5/25.5/26.5, 2023–2025 (n=540) | A v1 / B v2 / C E9 |

Primary lines are the candidates closest to 0.5 in the JSON, not hand-picked.
Halves use the frozen constants from the measured windows and are
presentation-only. The event-card target is used in K-IE and all trailing
yellow features. No 2026 rows were used for a design decision.
